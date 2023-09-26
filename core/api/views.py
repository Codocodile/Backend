from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from core.api.serializers import ChallengerSerializer, GroupSerializer, MembershipSerializer
from core.models import Group


class ChallengerCreateView(views.APIView):
    def post(self, request):
        serializer = ChallengerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TeamCreateAPIView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, ]


class MemberShipCreateAPIView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = (permissions.AllowAny,)
