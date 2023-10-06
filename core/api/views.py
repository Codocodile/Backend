from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from core.api.serializers import ChallengerSerializer, GroupSerializer, SendInvitationRequestSerializer
from core.models import Group, Challenger, Membership


class ChallengerCreateAPIView(generics.CreateAPIView):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerSerializer
    permission_classes = [permissions.AllowAny, ]


class GroupCreateAPIView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def perform_create(self, serializer):

        try:
            challenger = Challenger.objects.get(user=self.request.user)
        except Challenger.DoesNotExist:
            return Response(
                'No challenger with the id ({0}) found'.format(self.request.user.id),
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        group = serializer.save()
        membership = Membership(challenger=challenger, group=group, role="L", status="A")
        membership.save()

class InvitationRequestAPIView(generics.CreateAPIView):
    queryset = Membership.objects.all()
    serializer_class = SendInvitationRequestSerializer
    permission_classes = [permissions.IsAuthenticated, ]