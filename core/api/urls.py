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
    path('create-team/', views.GroupCreateAPIView.as_view(), name='add-challenger'),
    path('create-membership/', views.MemberShipCreateAPIView.as_view(), name='add-membership'),
]
