from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core.api import views

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-challenger/', views.ChallengerCreateAPIView.as_view(), name='add-challenger'),
    path('confirm-challenger/', views.ChallengerConfirmAPIView.as_view(), name='confirm-challenger'),
    path('update-challenger/', views.ChallengerUpdateAPIView.as_view(), name='update-challenger'),
    path('view-challenger/', views.ChallengerViewAPIView.as_view(), name='view-challenger'),
    path('search-challenger/', views.ChallengerSearchAPIView.as_view(), name='search-challenger'),
    path('team/', views.GroupAPIView.as_view(), name='team'),
    path('invitation/', views.InvitationRequestAPIView.as_view(), name='invitation'),
    path('accept-invitation/', views.InvitationAcceptanceAPIView.as_view(), name='accept-invitation'),
    path('password-reset/', views.PasswordResetAPIView.as_view(), name='password-reset'),
]
