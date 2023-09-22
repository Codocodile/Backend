from django.contrib.auth.models import User
from rest_framework import serializers

from core import models
from core.models import Challenger


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ChallengerSerializer(serializers.ModelSerializer):
    user = CurrentUserSerializer(many=False)

    class Meta:
        model = Challenger
        fields = ('user', 'status', 'bio')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        challenger = Challenger.objects.create(user=user, **validated_data)
        return challenger

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id  # Add the id to the representation
        return representation


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