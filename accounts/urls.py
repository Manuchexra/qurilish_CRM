from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('token/refresh/', views.refresh_token_view, name='token_refresh'),
    path('profile/', views.user_profile, name='user_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('check-auth/', views.check_auth, name='check_auth'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('register/', views.register_view, name='register'),
    path('users/<int:user_id>/activate/', views.activate_user, name='activate_user'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('users/pending/', views.PendingUsersListView.as_view(), name='pending_users'),
]