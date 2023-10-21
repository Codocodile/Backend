from random import choices
from django.conf import settings
from django.http import Http404
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from core.api.serializers import *
from core.models import Group, Challenger, Membership

from django.core.mail import send_mail
from django.db.models.functions import Concat
from django.db.models import Value as V
from django.db.models import Q
from django.db.models import Exists, OuterRef


class ChallengerCreateAPIView(generics.CreateAPIView):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerCreateSerializer
    permission_classes = [permissions.AllowAny, ]


class ChallengerViewAPIView(generics.RetrieveAPIView):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerViewSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        challenger = Challenger.objects.get(user=self.request.user)
        return challenger


class ChallengerUpdateAPIView(generics.UpdateAPIView):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        challenger = Challenger.objects.get(user=self.request.user)
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


class ChallengerSearchAPIView(generics.ListAPIView):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerSearchSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = Challenger.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(
                ~Exists(Membership.objects.filter(
                    challenger=OuterRef('pk'), status='A'))
            ).annotate(full_name=Concat(
                'user__first_name', V(' '), 'user__last_name')
            ).annotate(full_name_persian=Concat(
                'first_name_persian', V(' '), 'last_name_persian')
            ).filter(
                Q(full_name__icontains=name) |
                Q(full_name_persian__icontains=name)
            ).order_by('full_name_persian', 'full_name')
        return queryset


class GroupAPIView(views.APIView):
    queryset = Group.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        try:
            group = Membership.objects.filter(
                challenger__user=self.request.user, status='A').get().group
        except Membership.DoesNotExist:
            raise Http404
        return group

    def get(self, request):
        group = self.get_object()
        serializer = GroupViewSerializer(group)
        return Response(serializer.data)

    def post(self, request):
        challenger = Challenger.objects.get(user=self.request.user)
        membership = Membership.objects.filter(
            challenger=challenger, status='A')
        if membership.exists():
            raise serializers.ValidationError(
                "You are already member of a group.")
        group = Group(name=challenger.user.first_name +
                      " " + "Group", description="")
        group.save()
        membership = Membership(challenger=challenger,
                                group=group, role="L", status="A")
        membership.save()
        serializer = GroupViewSerializer(group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        group = self.get_object()
        serializer = GroupSerializer(data=request.data)
        if not serializer.is_valid():
            raise serializers.ValidationError("Data is not valid.")
        validated_data = serializer.validated_data
        group.name = validated_data['name']
        group.description = validated_data['description']
        group.save()
        serializer = GroupViewSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            membership = Membership.objects.filter(
                challenger__user=self.request.user, status='A').get()
        except Membership.DoesNotExist:
            raise Http404
        if membership.role != "L":
            membership.delete()
        else:
            group = membership.group
            group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvitationRequestAPIView(generics.ListCreateAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        queryset = Membership.objects.filter(
            challenger__user=self.request.user, status='P')
        return queryset

    def post(self, request):
        try:
            group = Membership.objects.get(
                challenger__user=self.request.user, status='A', role='L').group
        except Membership.DoesNotExist:
            raise serializers.ValidationError(
                "You are not leader of any group.")
        request.data['group'] = group.id
        return self.create(request)


class InvitationAcceptanceAPIView(generics.UpdateAPIView):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        try:
            membership = Membership.objects.filter(
                pk=self.request.data['id']).get()
        except Membership.DoesNotExist:
            raise Http404
        if membership.challenger.user != self.request.user:
            raise serializers.ValidationError(
                "You are not the target of this invitation.")
        if membership.status != "P":
            raise serializers.ValidationError(
                "This invitation is not pending.")
        return membership

    def put(self, request):
        if request.data['status'] != "A" and request.data['status'] != "R":
            raise serializers.ValidationError("Status is not valid.")
        membership = self.get_object()
        group = membership.group
        if Membership.objects.filter(group=group, status='A').count() >= 4:
            raise serializers.ValidationError("Group is full.")
        membership.status = request.data['status']
        membership.save()
        return Response(status=status.HTTP_200_OK)


class PasswordResetAPIView(views.APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request):
        challenger = Challenger.objects.filter(
            user__email=request.data['email']).last()
        if not challenger:
            raise Http404
        challenger.password_reset_code = ''.join(
            choices([str(i) for i in range(10)], k=17))
        challenger.save()
        send_mail(
            'Codocodile Password Reset',
            f'Your Codocodile password reset link is: https://codocodile.com/password-reset/{challenger.password_reset_code}',
            settings.EMAIL_HOST_USER,
            [challenger.user.email],
        )
        return Response(
            'Password reset code sent to the email address ({0})'.format(
                challenger.user.email),
            status=status.HTTP_200_OK
        )

    def put(self, request):
        try:
            challenger = Challenger.objects.get(
                user__email=request.data['email'])
        except Challenger.DoesNotExist:
            raise Http404
        if challenger.password_reset_code == request.data['token']:
            challenger.user.set_password(request.data['password'])
            challenger.user.save()
            return Response(
                'Password reset successfully',
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                'Password reset code is not correct',
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
