from django.urls import path
from . import views

app_name = 'gamerank_core'

urlpatterns = [
    path('', views.GameListView.as_view(), name='home'),
    path('game/<str:pk>/', views.GameDetailView.as_view(), name='game_detail'),
    path('game/<str:pk>/htmx/', views.GameDetailHTMXView.as_view(), name='game_detail_htmx'),
    path('game/<str:pk>.json', views.game_json_endpoint, name='game_json'),
    path('game/<str:pk>/action/', views.GameActionView.as_view(), name='game_action'),
    # Add other core URLs here (e.g., vote, follow, comment actions)
] 