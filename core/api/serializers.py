from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers

from core import models
from core.models import Challenger, Membership


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'password', 'email')

    def validate_password(self, value: str) -> str:
        return make_password(value)


class ChallengerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Challenger
        fields = ('id', 'user', 'firstـname_persian', 'lastـname_persian',
                  'phone_number', 'status', 'gender', 'is_workshop_attender')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        challenger = Challenger.objects.create(user=user, **validated_data)
        return challenger


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ('name', 'description')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id
        return representation


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Membership
        fields = ('challenger', 'group')

    def validate_group(self, data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        try:
            challenger = Challenger.objects.get(user=user)
            membership = Membership.objects.get(challenger=challenger)
        except Challenger.DoesNotExist:
            raise serializers.ValidationError(
                'No challenger with the id ({0}) found'.format(user.id))
        except Membership.DoesNotExist:
            raise serializers.ValidationError("You don't have any group.")
        if membership.role != "L":
            raise serializers.ValidationError(
                "You are not Leader of the group.")
        if data["group"] != membership.group:
            raise serializers.ValidationError(
                "You are not member of the group whit id ({0}).".format(data["group"].id))
        return data
