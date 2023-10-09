from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers

import re

from core import models
from core.models import Challenger, Membership


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password', 'email')

    def validate_password(self, value: str) -> str:
        return make_password(value)

class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ChallengerCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()

    class Meta:
        model = Challenger
        fields = ('user', 'first_name_persian', 'last_name_persian',
                  'phone_number', 'status', 'gender', 'is_workshop_attender')
    
    def validate_phone_number(self, value: str) -> str:
        if re.match(r'^09\d{9}$', value):
            return value
        raise serializers.ValidationError("Phone number is not valid.")
    
    def validate_status(self, value: str) -> str:
        if value in ['J', 'S', 'P']:
            return value
        raise serializers.ValidationError("Status is not valid.")
    
    def validate_gender(self, value: str) -> str:
        if value in ['M', 'F']:
            return value
        raise serializers.ValidationError("Gender is not valid.")

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        challenger = Challenger.objects.create(user=user, **validated_data)
        return challenger

class ChallengerViewSerializer(serializers.ModelSerializer):
    user = UserViewSerializer()

    class Meta:
        model = Challenger
        fields = ('id', 'user', 'first_name_persian', 'last_name_persian',
                  'phone_number', 'status', 'gender', 'is_workshop_attender', 'profile_pic', 'bio')


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
                "You are not member of the group with id ({0}).".format(data["group"].id))
        return data
