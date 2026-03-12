"""
Database Models for Community Maintenance AI System.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom user model with role-based access."""
    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('admin', 'Admin'),
        ('technician', 'Technician'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    block = models.CharField(max_length=50, blank=True, null=True)
    flat_number = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    specialization = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="For technicians: e.g., Plumbing, Electrical, Elevator"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="For technicians: availability status"
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        db_table = 'users'


class Complaint(models.Model):
    """Complaint model with AI-driven fields."""
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    
    CATEGORY_CHOICES = [
        ('Electrical', 'Electrical'),
        ('Plumbing', 'Plumbing'),
        ('Elevator', 'Elevator'),
        ('Security', 'Security'),
        ('Cleanliness', 'Cleanliness'),
        ('Carpentry', 'Carpentry'),
    ]
    
    resident = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='complaints'
    )
    description = models.TextField()
    location = models.CharField(max_length=100)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True
    )
    ai_category = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="AI-predicted category"
    )
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default='Medium'
    )
    ai_priority = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="AI-suggested priority"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Open'
    )
    assigned_staff = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_complaints',
        limit_choices_to={'role': 'technician'}
    )
    is_duplicate = models.BooleanField(default=False)
    master_complaint = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='duplicates',
        help_text="If duplicate, reference to the master complaint"
    )
    similarity_score = models.FloatField(null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    ai_explanation = models.TextField(
        blank=True, null=True,
        help_text="Explainable AI reasoning for classification/priority"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Complaint #{self.id} - {self.category} [{self.status}]"
    
    class Meta:
        db_table = 'complaints'
        ordering = ['-created_at']


class Asset(models.Model):
    """Community assets for tracking maintenance."""
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    install_date = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default='Operational')
    
    def __str__(self):
        return f"{self.name} ({self.location})"
    
    class Meta:
        db_table = 'assets'


class MaintenanceLog(models.Model):
    """Maintenance event log for predictive analysis."""
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name='maintenance_logs',
        null=True, blank=True
    )
    asset_name = models.CharField(max_length=200)
    maintenance_type = models.CharField(max_length=50)
    action_taken = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    downtime_hours = models.FloatField(default=0)
    technician = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'technician'}
    )
    
    def __str__(self):
        return f"{self.asset_name} - {self.maintenance_type} ({self.date})"
    
    class Meta:
        db_table = 'maintenance_logs'
        ordering = ['-date']


class Feedback(models.Model):
    """Resident feedback for complaints."""
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name='feedbacks'
    )
    resident = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='feedbacks'
    )
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    sentiment_label = models.CharField(max_length=20, blank=True, null=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for Complaint #{self.complaint_id} - {self.rating}/5"
    
    class Meta:
        db_table = 'feedback'


class Notification(models.Model):
    """Notification system for admins, residents, and technicians."""
    NOTIFICATION_TYPES = [
        ('complaint_assigned', 'Complaint Assigned'),
        ('complaint_updated', 'Complaint Updated'),
        ('complaint_resolved', 'Complaint Resolved'),
        ('maintenance_alert', 'Maintenance Alert'),
        ('duplicate_detected', 'Duplicate Detected'),
        ('root_cause_alert', 'Root Cause Alert'),
    ]
    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"[{self.notification_type}] {self.title}"
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']


class Prediction(models.Model):
    """Store AI predictions for dashboard."""
    asset_name = models.CharField(max_length=200)
    predicted_failure_date = models.DateField()
    suggested_preventive_date = models.DateField()
    risk_level = models.CharField(max_length=20)
    confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.asset_name} - Predicted: {self.predicted_failure_date}"
    
    class Meta:
        db_table = 'predictions'
        ordering = ['-created_at']
