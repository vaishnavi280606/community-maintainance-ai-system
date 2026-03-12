"""
REST API Views for Community Maintenance AI System.
"""

from django.utils import timezone
from django.db.models import Count, Avg, F, Q
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Complaint, Feedback, Notification, Prediction, MaintenanceLog
from .serializers import (
    UserRegistrationSerializer, UserSerializer, UserLoginSerializer,
    ComplaintSerializer, ComplaintCreateSerializer, ComplaintUpdateSerializer,
    FeedbackSerializer, FeedbackCreateSerializer,
    NotificationSerializer, PredictionSerializer,
    DashboardStatsSerializer, PredictCategorySerializer, DetectDuplicateSerializer,
)
from .services.complaint_service import process_new_complaint, update_complaint_status, assign_technician_to_complaint

User = get_user_model()


# ─── Authentication ───────────────────────────────────────────────────

class RegisterView(APIView):
    """POST /auth/register — Create a new user."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """POST /auth/login — Authenticate user and return JWT tokens."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class ProfileView(APIView):
    """GET /auth/profile — Get current user profile.
       PATCH /auth/profile — Update current user profile."""
    
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        allowed = ['first_name', 'last_name', 'email', 'phone', 'block', 'flat_number']
        if user.role == 'technician':
            allowed += ['specialization', 'is_available']
        for field in allowed:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        return Response(UserSerializer(user).data)


# ─── Complaints ───────────────────────────────────────────────────────

class ComplaintListCreateView(APIView):
    """
    GET  /complaints — List complaints (filtered by role)
    POST /complaints — Submit a new complaint
    """
    
    def get(self, request):
        user = request.user
        
        if user.role == 'resident':
            complaints = Complaint.objects.filter(resident=user)
        elif user.role == 'technician':
            complaints = Complaint.objects.filter(assigned_staff=user)
        else:  # admin
            complaints = Complaint.objects.all()
        
        # Optional filters
        category = request.query_params.get('category')
        status_filter = request.query_params.get('status')
        priority = request.query_params.get('priority')
        location = request.query_params.get('location')
        
        if category:
            complaints = complaints.filter(category=category)
        if status_filter:
            complaints = complaints.filter(status=status_filter)
        if priority:
            complaints = complaints.filter(priority=priority)
        if location:
            complaints = complaints.filter(location=location)
        
        serializer = ComplaintSerializer(complaints, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ComplaintCreateSerializer(data=request.data)
        if serializer.is_valid():
            complaint = serializer.save(resident=request.user)
            
            # Process through AI pipeline
            try:
                complaint = process_new_complaint(complaint)
            except Exception as e:
                # If AI processing fails, save the complaint anyway
                complaint.ai_explanation = f"AI processing error: {str(e)}"
                complaint.save()
            
            return Response(
                ComplaintSerializer(complaint).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComplaintDetailView(APIView):
    """
    GET    /complaints/<id> — Get complaint details
    PATCH  /complaints/<id> — Update complaint
    """
    
    def get(self, request, pk):
        try:
            complaint = Complaint.objects.get(pk=pk)
        except Complaint.DoesNotExist:
            return Response(
                {'error': 'Complaint not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(ComplaintSerializer(complaint).data)
    
    def patch(self, request, pk):
        try:
            complaint = Complaint.objects.get(pk=pk)
        except Complaint.DoesNotExist:
            return Response(
                {'error': 'Complaint not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if request.user.role not in ['admin', 'technician']:
            return Response(
                {'error': 'Only admins and technicians can update complaints'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status:
            update_complaint_status(complaint, new_status)
        
        serializer = ComplaintUpdateSerializer(complaint, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ComplaintSerializer(complaint).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── AI Endpoints ─────────────────────────────────────────────────────

class PredictCategoryView(APIView):
    """POST /predict-category — Predict complaint category from text."""
    
    def post(self, request):
        serializer = PredictCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        text = serializer.validated_data['text']
        
        try:
            from .services.ai_service import classify_complaint
            result = classify_complaint(text)
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DetectDuplicateView(APIView):
    """POST /detect-duplicate — Check if a complaint is a duplicate."""
    
    def post(self, request):
        serializer = DetectDuplicateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        text = serializer.validated_data['text']
        
        try:
            from .services.ai_service import check_duplicate
            existing = list(
                Complaint.objects.exclude(status='Closed')
                .values('id', 'description')
            )
            existing_for_check = [
                {'complaint_id': str(c['id']), 'description': c['description']}
                for c in existing
            ]
            result = check_duplicate(text, existing_for_check)
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ─── Dashboard & Analytics ────────────────────────────────────────────

class DashboardStatsView(APIView):
    """GET /dashboard-stats — Get dashboard statistics for admin."""
    
    def get(self, request):
        complaints = Complaint.objects.all()
        
        # Basic stats
        total = complaints.count()
        open_count = complaints.filter(status='Open').count()
        resolved_count = complaints.filter(status__in=['Resolved', 'Closed']).count()
        in_progress = complaints.filter(status='In Progress').count()
        assigned_count = complaints.filter(status='Assigned').count()
        
        # Category distribution
        category_dist = dict(
            complaints.values('category')
            .annotate(count=Count('id'))
            .values_list('category', 'count')
        )
        
        # Priority distribution
        priority_dist = dict(
            complaints.values('priority')
            .annotate(count=Count('id'))
            .values_list('priority', 'count')
        )
        
        # Status distribution
        status_dist = dict(
            complaints.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        
        # Recent complaints
        recent = complaints[:10]
        
        # Average resolution time
        resolved_with_time = complaints.filter(
            resolved_at__isnull=False
        )
        if resolved_with_time.exists():
            avg_hours = resolved_with_time.annotate(
                resolution_time=F('resolved_at') - F('created_at')
            ).aggregate(avg=Avg('resolution_time'))
            avg_resolution = avg_hours['avg'].total_seconds() / 3600 if avg_hours['avg'] else 0
        else:
            avg_resolution = 0
        
        # Location distribution
        location_dist = dict(
            complaints.values('location')
            .annotate(count=Count('id'))
            .values_list('location', 'count')
        )
        
        # Monthly trend (last 6 months)
        from django.db.models.functions import TruncMonth
        monthly_trend = list(
            complaints.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
            .values('month', 'count')
        )
        # Convert datetime to string
        for item in monthly_trend:
            item['month'] = item['month'].strftime('%Y-%m') if item['month'] else ''
        
        return Response({
            'total_complaints': total,
            'open_complaints': open_count,
            'assigned_complaints': assigned_count,
            'resolved_complaints': resolved_count,
            'in_progress_complaints': in_progress,
            'category_distribution': category_dist,
            'priority_distribution': priority_dist,
            'status_distribution': status_dist,
            'location_distribution': location_dist,
            'monthly_trend': monthly_trend,
            'recent_complaints': ComplaintSerializer(recent, many=True).data,
            'avg_resolution_time_hours': round(avg_resolution, 1),
        })


class RootCauseView(APIView):
    """GET /root-cause — Get root cause analysis."""
    
    def get(self, request):
        try:
            from .services.ai_service import get_root_cause_analysis
            results = get_root_cause_analysis()
            return Response(results)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RSIView(APIView):
    """GET /rsi — Get Resident Satisfaction Index."""
    
    def get(self, request):
        try:
            from .services.ai_service import get_rsi_heatmap
            data = get_rsi_heatmap()
            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MaintenancePredictionsView(APIView):
    """GET /maintenance-predictions — Get predictive maintenance data."""
    
    def get(self, request):
        try:
            from .services.ai_service import get_maintenance_recommendations
            data = get_maintenance_recommendations()
            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ─── Feedback ─────────────────────────────────────────────────────────

class FeedbackListCreateView(APIView):
    """
    GET  /feedback — List feedback
    POST /feedback — Submit feedback
    """
    
    def get(self, request):
        if request.user.role == 'admin':
            feedbacks = Feedback.objects.all()
        else:
            feedbacks = Feedback.objects.filter(resident=request.user)
        
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FeedbackCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            complaint = Complaint.objects.get(pk=serializer.validated_data['complaint_id'])
        except Complaint.DoesNotExist:
            return Response(
                {'error': 'Complaint not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Analyze sentiment
        from .services.ai_service import analyze_sentiment as ai_sentiment
        comment = serializer.validated_data.get('comment', '')
        sentiment = ai_sentiment(comment) if comment else {'label': 'Neutral', 'compound': 0.0}
        
        feedback = Feedback.objects.create(
            complaint=complaint,
            resident=request.user,
            rating=serializer.validated_data['rating'],
            comment=comment,
            sentiment_label=sentiment['label'],
            sentiment_score=sentiment['compound'],
        )
        
        return Response(
            FeedbackSerializer(feedback).data,
            status=status.HTTP_201_CREATED
        )


# ─── Notifications ────────────────────────────────────────────────────

class NotificationListView(APIView):
    """GET /notifications — Get user's notifications."""
    
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        unread_only = request.query_params.get('unread')
        if unread_only:
            notifications = notifications.filter(is_read=False)
        
        serializer = NotificationSerializer(notifications[:50], many=True)
        return Response({
            'notifications': serializer.data,
            'unread_count': Notification.objects.filter(
                user=request.user, is_read=False
            ).count()
        })


class NotificationMarkReadView(APIView):
    """POST /notifications/<id>/read — Mark notification as read."""
    
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'status': 'ok'})
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MarkAllNotificationsReadView(APIView):
    """POST /notifications/mark-all-read — Mark all notifications as read."""
    
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'ok'})


# ─── Technician Views ─────────────────────────────────────────────────

class TechnicianListView(APIView):
    """
    GET  /technicians — List all technicians (admin only).
    POST /technicians — Create a new technician (admin only).
    """
    
    def get(self, request):
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        technicians = User.objects.filter(role='technician')
        data = []
        for tech in technicians:
            active_count = Complaint.objects.filter(
                assigned_staff=tech,
                status__in=['Assigned', 'In Progress']
            ).count()
            resolved_count = Complaint.objects.filter(
                assigned_staff=tech,
                status__in=['Resolved', 'Closed']
            ).count()
            
            data.append({
                **UserSerializer(tech).data,
                'active_tasks': active_count,
                'resolved_tasks': resolved_count,
            })
        
        return Response(data)

    def post(self, request):
        if request.user.role != 'admin':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        data['role'] = 'technician'
        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            tech = serializer.save()
            return Response(UserSerializer(tech).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TechnicianDetailView(APIView):
    """
    PATCH  /technicians/<id> — Update technician details (admin only).
    DELETE /technicians/<id> — Remove a technician (admin only).
    """

    def patch(self, request, pk):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        try:
            tech = User.objects.get(pk=pk, role='technician')
        except User.DoesNotExist:
            return Response({'error': 'Technician not found'}, status=status.HTTP_404_NOT_FOUND)

        allowed = ['first_name', 'last_name', 'email', 'phone', 'specialization', 'is_available', 'block']
        for field in allowed:
            if field in request.data:
                setattr(tech, field, request.data[field])
        tech.save()
        return Response(UserSerializer(tech).data)

    def delete(self, request, pk):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        try:
            tech = User.objects.get(pk=pk, role='technician')
        except User.DoesNotExist:
            return Response({'error': 'Technician not found'}, status=status.HTTP_404_NOT_FOUND)

        # Re-assign any active complaints back to Open
        active = Complaint.objects.filter(assigned_staff=tech, status__in=['Assigned', 'In Progress'])
        active.update(assigned_staff=None, status='Open')

        tech.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)


class AssignTechnicianView(APIView):
    """POST /complaints/<id>/assign — Admin assigns a technician to a complaint."""

    def post(self, request, pk):
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            complaint = Complaint.objects.get(pk=pk)
        except Complaint.DoesNotExist:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)
        
        technician_id = request.data.get('technician_id')
        if not technician_id:
            return Response({'error': 'technician_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            technician = User.objects.get(pk=technician_id, role='technician')
        except User.DoesNotExist:
            return Response({'error': 'Technician not found'}, status=status.HTTP_404_NOT_FOUND)
        
        complaint = assign_technician_to_complaint(complaint, technician)
        return Response(ComplaintSerializer(complaint).data)
