from django.urls import path
from . import views

app_name = 'gamerank_users'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('user/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('user/votes/', views.UserVotesView.as_view(), name='user_votes'),
    path('user/follows/', views.UserFollowsView.as_view(), name='user_follows'),
    path('settings/', views.UserSettingsView.as_view(), name='user_settings'),
    # Add other user-related URLs here
] 