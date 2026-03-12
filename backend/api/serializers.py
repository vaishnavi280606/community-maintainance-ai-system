"""
REST API Serializers for Community Maintenance AI System.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Complaint, Asset, MaintenanceLog, Feedback, Notification, Prediction

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name',
                  'role', 'block', 'flat_number', 'phone', 'specialization']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user display."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'role', 'block', 'flat_number', 'phone', 'specialization',
                  'is_available']


class UserLoginSerializer(serializers.Serializer):
    """Serializer for login."""
    username = serializers.CharField()
    password = serializers.CharField()


class ComplaintSerializer(serializers.ModelSerializer):
    """Serializer for complaints."""
    resident_name = serializers.CharField(source='resident.get_full_name', read_only=True)
    assigned_staff_name = serializers.CharField(
        source='assigned_staff.get_full_name', read_only=True, default=None
    )
    
    class Meta:
        model = Complaint
        fields = [
            'id', 'resident', 'resident_name', 'description', 'location',
            'category', 'ai_category', 'priority', 'ai_priority', 'status',
            'assigned_staff', 'assigned_staff_name', 'is_duplicate',
            'master_complaint', 'similarity_score', 'sentiment_score',
            'ai_explanation', 'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = [
            'ai_category', 'ai_priority', 'is_duplicate', 'master_complaint',
            'similarity_score', 'sentiment_score', 'ai_explanation',
            'created_at', 'updated_at', 'resolved_at'
        ]


class ComplaintCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating complaints (resident submits)."""
    class Meta:
        model = Complaint
        fields = ['description', 'location']


class ComplaintUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating complaint status."""
    class Meta:
        model = Complaint
        fields = ['status', 'assigned_staff', 'priority', 'category']


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for feedback."""
    resident_name = serializers.CharField(source='resident.get_full_name', read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'complaint', 'resident', 'resident_name', 'rating',
                  'comment', 'sentiment_label', 'sentiment_score', 'created_at']
        read_only_fields = ['sentiment_label', 'sentiment_score', 'created_at']


class FeedbackCreateSerializer(serializers.Serializer):
    """Serializer for submitting feedback."""
    complaint_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, default='')


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read',
                  'complaint', 'created_at']
        read_only_fields = ['created_at']


class PredictionSerializer(serializers.ModelSerializer):
    """Serializer for maintenance predictions."""
    class Meta:
        model = Prediction
        fields = '__all__'


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    total_complaints = serializers.IntegerField()
    open_complaints = serializers.IntegerField()
    resolved_complaints = serializers.IntegerField()
    in_progress_complaints = serializers.IntegerField()
    category_distribution = serializers.DictField()
    priority_distribution = serializers.DictField()
    status_distribution = serializers.DictField()
    recent_complaints = ComplaintSerializer(many=True)
    avg_resolution_time_hours = serializers.FloatField()


class PredictCategorySerializer(serializers.Serializer):
    """Serializer for AI category prediction request."""
    text = serializers.CharField()


class DetectDuplicateSerializer(serializers.Serializer):
    """Serializer for duplicate detection request."""
    text = serializers.CharField()
