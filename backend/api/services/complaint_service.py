"""
Complaint Service — handles complaint lifecycle:
- AI classification on submission
- Duplicate detection
- AI-suggested technician (admin approves)
- Notification dispatch
"""

from django.utils import timezone
from django.db.models import Q, Count

from api.models import Complaint, User, Notification
from api.services.ai_service import classify_complaint, check_duplicate


# Category → Specialization mapping for technician matching
CATEGORY_SPECIALIZATION_MAP = {
    'Electrical': 'Electrical',
    'Plumbing': 'Plumbing',
    'Elevator': 'Elevator',
    'Security': 'Security',
    'Cleanliness': 'Cleanliness',
    'Carpentry': 'Carpentry',
}


def process_new_complaint(complaint: Complaint) -> Complaint:
    """
    Full processing pipeline for a new complaint:
    1. AI classification (category + priority)
    2. Duplicate detection
    3. Suggest best technician (notify admin for approval)
    4. Send notifications — status stays 'Open' until admin assigns
    """
    # Step 1: AI Classification
    ai_result = classify_complaint(complaint.description)
    complaint.ai_category = ai_result['category']
    complaint.ai_priority = ai_result['priority']
    complaint.sentiment_score = ai_result['sentiment']['compound']
    complaint.ai_explanation = ai_result['explanation']
    
    # Set category and priority from AI if not manually set
    if not complaint.category:
        complaint.category = ai_result['category']
    if complaint.priority == 'Medium':  # default
        complaint.priority = ai_result['priority']
    
    # Step 2: Duplicate Detection
    existing_complaints = list(
        Complaint.objects.exclude(id=complaint.id)
        .exclude(status='Closed')
        .values('id', 'description')
    )
    existing_for_check = [
        {'complaint_id': str(c['id']), 'description': c['description']}
        for c in existing_complaints
    ]
    
    if existing_for_check:
        dup_result = check_duplicate(complaint.description, existing_for_check)
        if dup_result['is_duplicate']:
            complaint.is_duplicate = True
            complaint.similarity_score = dup_result['similarity_score']
            try:
                master_id = int(dup_result['similar_complaint_id'])
                complaint.master_complaint_id = master_id
            except (ValueError, TypeError):
                pass
    
    # Step 3: Find best technician as SUGGESTION (do NOT auto-assign)
    suggested_technician = None
    if not complaint.is_duplicate:
        suggested_technician = _find_best_technician(complaint.category, complaint.location)
    
    # Keep status as 'Open' — admin will assign manually
    complaint.status = 'Open'
    complaint.save()
    
    # Step 4: Send notifications (with suggestion for admin)
    _send_complaint_notifications(complaint, suggested_technician)
    
    return complaint


def _find_best_technician(category: str, location: str) -> User:
    """
    Find the best available technician based on:
    1. Specialization matching the complaint category
    2. Availability
    3. Current workload (least assigned complaints)
    Returns a suggestion — does NOT assign.
    """
    specialization = CATEGORY_SPECIALIZATION_MAP.get(category, '')
    
    # Find available technicians with matching specialization
    technicians = User.objects.filter(
        role='technician',
        is_available=True
    )
    
    if specialization:
        # Prefer specialization match
        specialized = technicians.filter(
            specialization__icontains=specialization
        )
        if specialized.exists():
            technicians = specialized
    
    if not technicians.exists():
        return None
    
    # Pick the one with fewest active assignments
    technicians = technicians.annotate(
        active_count=Count(
            'assigned_complaints',
            filter=Q(assigned_complaints__status__in=['Assigned', 'In Progress'])
        )
    ).order_by('active_count')
    
    return technicians.first()


def assign_technician_to_complaint(complaint: Complaint, technician: User) -> Complaint:
    """
    Admin assigns a technician to a complaint.
    Sets status to 'Assigned' and sends notifications.
    """
    complaint.assigned_staff = technician
    complaint.status = 'Assigned'
    complaint.save()

    notifications = []

    # Notify the assigned technician
    notifications.append(Notification(
        user=technician,
        notification_type='complaint_assigned',
        title=f'New Task Assigned: {complaint.category}',
        message=(
            f'You have been assigned a {complaint.priority} priority '
            f'{complaint.category} complaint at {complaint.location}: '
            f'"{complaint.description[:100]}..."'
        ),
        complaint=complaint
    ))

    # Notify the resident
    notifications.append(Notification(
        user=complaint.resident,
        notification_type='complaint_updated',
        title='Technician Assigned to Your Complaint',
        message=(
            f'Your complaint #{complaint.id} ({complaint.category}) has been '
            f'assigned to {technician.get_full_name()}. '
            f'Status updated to Assigned.'
        ),
        complaint=complaint
    ))

    Notification.objects.bulk_create(notifications)
    return complaint


def _send_complaint_notifications(complaint: Complaint, suggested_technician=None):
    """Send notifications to relevant users."""
    notifications = []
    
    # Notify all admins about new complaint with AI suggestion
    admins = User.objects.filter(role='admin')
    suggestion_text = (
        f'AI suggests assigning to {suggested_technician.get_full_name()} '
        f'({suggested_technician.specialization}). '
        f'Please review and assign from the Complaints page.'
    ) if suggested_technician else 'No matching technician found. Please assign manually.'
    
    for admin in admins:
        notifications.append(Notification(
            user=admin,
            notification_type='complaint_updated',
            title=f'🆕 New {complaint.priority} Priority Complaint — Action Required',
            message=(
                f'New {complaint.category} complaint at {complaint.location}: '
                f'"{complaint.description[:100]}..." — '
                f'{suggestion_text}'
            ),
            complaint=complaint
        ))
    
    # Notify resident about submission
    notifications.append(Notification(
        user=complaint.resident,
        notification_type='complaint_updated',
        title='Complaint Received',
        message=(
            f'Your complaint has been received and classified as {complaint.category} '
            f'with {complaint.priority} priority. '
            f'An admin will review and assign a technician shortly.'
        ),
        complaint=complaint
    ))
    
    # If duplicate detected, notify admin
    if complaint.is_duplicate:
        for admin in admins:
            notifications.append(Notification(
                user=admin,
                notification_type='duplicate_detected',
                title='Duplicate Complaint Detected',
                message=(
                    f'Complaint #{complaint.id} appears to be a duplicate of '
                    f'Complaint #{complaint.master_complaint_id} '
                    f'(similarity: {complaint.similarity_score:.2f})'
                ),
                complaint=complaint
            ))
    
    Notification.objects.bulk_create(notifications)


def update_complaint_status(complaint: Complaint, new_status: str):
    """Update complaint status and send notifications."""
    old_status = complaint.status
    complaint.status = new_status
    
    if new_status == 'Resolved':
        complaint.resolved_at = timezone.now()
    
    complaint.save()
    
    # Notify resident
    Notification.objects.create(
        user=complaint.resident,
        notification_type='complaint_resolved' if new_status == 'Resolved' else 'complaint_updated',
        title=f'Complaint Status Updated: {new_status}',
        message=(
            f'Your complaint #{complaint.id} ({complaint.category}) has been '
            f'updated from {old_status} to {new_status}.'
        ),
        complaint=complaint
    )
