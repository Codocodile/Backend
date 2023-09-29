from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers

from core import models
from core.models import Challenger


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'firstname', 'lastname', 'username', 'password', 'email')

    def validate_password(self, value: str) -> str:
        return make_password(value)


class ChallengerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Challenger
        fields = ('id', 'user', 'status', 'bio')

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
        representation['id'] = instance.id  # Add the id to the representation
        return representation


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Membership
        fields = ('challenger', 'group', 'role', 'status')