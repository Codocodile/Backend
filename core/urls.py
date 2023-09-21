from django.urls import path

from core import views

urlpatterns = [
    path('', views.ApiOverview, name='home'),
    path('create-challenger/', views.ChallengerCreateAPIView.as_view(), name='add-challenger'),
    path('create-team/', views.TeamCreateAPIView.as_view(), name='add-challenger')
]
