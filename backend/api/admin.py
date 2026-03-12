from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Complaint, Asset, MaintenanceLog, Feedback, Notification, Prediction


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'block', 'flat_number', 'is_available']
    list_filter = ['role', 'block', 'is_available']
    fieldsets = UserAdmin.fieldsets + (
        ('Community Info', {'fields': ('role', 'block', 'flat_number', 'phone', 'specialization', 'is_available')}),
    )


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'priority', 'status', 'location', 'assigned_staff', 'created_at']
    list_filter = ['category', 'priority', 'status', 'location']
    search_fields = ['description']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset_type', 'location', 'status']


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ['asset_name', 'maintenance_type', 'date', 'cost', 'downtime_hours']
    list_filter = ['maintenance_type', 'asset_name']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'resident', 'rating', 'sentiment_label', 'created_at']
    list_filter = ['sentiment_label', 'rating']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['asset_name', 'predicted_failure_date', 'risk_level', 'created_at']
