from random import choices
from django.conf import settings
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from core.api.serializers import ChallengerCreateSerializer, ChallengerViewSerializer, ChallengerUpdateSerializer, GroupSerializer, MembershipSerializer
from core.models import Group, Challenger, Membership

from django.core.mail import send_mail


class ChallengerCreateAPIView(generics.CreateAPIView):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerCreateSerializer
    permission_classes = [permissions.AllowAny, ]


class ChallengerViewAPIView(generics.RetrieveAPIView):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerViewSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        try:
            challenger = Challenger.objects.get(user=self.request.user)
        except Challenger.DoesNotExist:
            return Response(
                'No challenger with the id ({0}) found'.format(
                    self.request.user.id),
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        return challenger


class ChallengerUpdateAPIView(generics.UpdateAPIView):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        try:
            challenger = Challenger.objects.get(user=self.request.user)
        except Challenger.DoesNotExist:
            return Response(
                'No challenger with the id ({0}) found'.format(
                    self.request.user.id),
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        return challenger


class ChallengerConfirmAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        challenger = Challenger.objects.get(user=request.user)
        challenger.confirmation_code = ''.join(
            choices([str(i) for i in range(10)], k=5))
        challenger.save()
        send_mail(
            'Codocodile Confirmation Code',
            'Your Codocodile confirmation code is {0}. Ignore this email if you\'re not a particpant.'.format(
                challenger.confirmation_code),
            settings.EMAIL_HOST_USER,
            [challenger.user.email],
        )
        return Response(
            'Confirmation code sent to the email address ({0})'.format(
                challenger.user.email),
            status=status.HTTP_200_OK
        )

    def post(self, request):
        challenger = Challenger.objects.get(user=request.user)
        if challenger.confirmation_code == request.data['confirmation_code']:
            challenger.is_confirmed = True
            challenger.save()
            return Response(
                'Challenger confirmed successfully',
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                'Confirmation code is not correct',
                status=status.HTTP_406_NOT_ACCEPTABLE
            )


class GroupCreateAPIView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def perform_create(self, serializer):
        try:
            challenger = Challenger.objects.get(user=self.request.user)
        except Challenger.DoesNotExist:
            return Response(
                'No challenger with the id ({0}) found'.format(
                    self.request.user.id),
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        group = serializer.save()
        membership = Membership(challenger=challenger,
                                group=group, role="L", status="A")
        membership.save()


class InvitationRequestAPIView(generics.CreateAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated, ]


class InvitationAcceptanceAPIView(generics.UpdateAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated, ]
