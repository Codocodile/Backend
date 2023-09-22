from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.api.serializers import ChallengerSerializer, GroupSerializer, MembershipSerializer
from core.models import Challenger, Group


# Create your views here.
@api_view(['Get'])
def ApiOverview(request):
    api_urls = {
        'add_user': '/add-user',
        'update_user': '/update_user',
        'delete_user': '/delete-user',
        'add_team': '/add-team',
        'update-team': '/update-team',
        'delete-team': '/delete-team',
    }

    return Response(api_urls)


class UserCreateAPIView(generics.CreateAPIView):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerSerializer
    permission_classes = (AllowAny,)


class TeamCreateAPIView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (AllowAny,)


class MemberShipCreateAPIView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = (AllowAny,)
