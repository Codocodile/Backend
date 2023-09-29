from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from core.api.serializers import ChallengerSerializer, GroupSerializer, MembershipSerializer
from core.models import Group, Challenger


class ChallengerCreateAPIView(generics.CreateAPIView):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerSerializer
    permission_classes = [permissions.AllowAny, ]


class TeamCreateAPIView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, ]


class MemberShipCreateAPIView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = (permissions.AllowAny,)
