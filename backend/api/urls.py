"""
URL Configuration for the API app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Authentication
    path('auth/register', views.RegisterView.as_view(), name='register'),
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile', views.ProfileView.as_view(), name='profile'),
    
    # Complaints
    path('complaints', views.ComplaintListCreateView.as_view(), name='complaints'),
    path('complaints/<int:pk>', views.ComplaintDetailView.as_view(), name='complaint-detail'),
    path('complaints/<int:pk>/assign', views.AssignTechnicianView.as_view(), name='assign-technician'),
    
    # AI Endpoints
    path('predict-category', views.PredictCategoryView.as_view(), name='predict-category'),
    path('detect-duplicate', views.DetectDuplicateView.as_view(), name='detect-duplicate'),
    
    # Dashboard & Analytics
    path('dashboard-stats', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('root-cause', views.RootCauseView.as_view(), name='root-cause'),
    path('rsi', views.RSIView.as_view(), name='rsi'),
    path('maintenance-predictions', views.MaintenancePredictionsView.as_view(),
         name='maintenance-predictions'),
    
    # Feedback
    path('feedback', views.FeedbackListCreateView.as_view(), name='feedback'),
    
    # Notifications
    path('notifications', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read', views.NotificationMarkReadView.as_view(),
         name='notification-read'),
    path('notifications/mark-all-read', views.MarkAllNotificationsReadView.as_view(),
         name='notifications-mark-all-read'),
    
    # Technicians
    path('technicians', views.TechnicianListView.as_view(), name='technicians'),
    path('technicians/<int:pk>', views.TechnicianDetailView.as_view(), name='technician-detail'),
]
