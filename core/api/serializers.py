from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers

import re

from core import models
from core.models import Challenger, Membership, Group


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password', 'email')

    def validate_password(self, value: str) -> str:
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError(
                "Password must contain at least one digit.")
        if not re.search(r'[^A-Za-z0-9]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character.")
        return make_password(value)


class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


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
        user_data['username'] = validated_data['phone_number']
        user = User.objects.create(**user_data)
        challenger = Challenger.objects.create(user=user, **validated_data)
        return challenger


class ChallengerViewSerializer(serializers.ModelSerializer):
    user = UserViewSerializer()

    class Meta:
        model = Challenger
        fields = ('id', 'user', 'first_name_persian', 'last_name_persian',
                  'phone_number', 'status', 'gender', 'is_workshop_attender', 'profile_pic', 'bio', 'is_confirmed', 'national_code', 'university')


class ChallengerSearchSerializer(serializers.ModelSerializer):
    user = UserSearchSerializer()

    class Meta:
        model = Challenger
        fields = ('id', 'user', 'first_name_persian',
                  'last_name_persian', 'status', 'university')


class ChallengerUpdateSerializer(serializers.ModelSerializer):
    user = UserViewSerializer()

    class Meta:
        model = Challenger
        fields = ('user', 'first_name_persian', 'last_name_persian',
                  'status', 'gender', 'is_workshop_attender', 'bio', 'national_code', 'university')

    def validate_status(self, value: str) -> str:
        if value in ['J', 'S', 'P']:
            return value
        raise serializers.ValidationError("Status is not valid.")

    def validate_gender(self, value: str) -> str:
        if value in ['M', 'F']:
            return value
        raise serializers.ValidationError("Gender is not valid.")

    def validate_national_code(self, value: str) -> str:
        if value == '':
            return value
        if re.match(r'^\d{8}|\d{9}|\d{10}$', value):
            if len(value) < 10:
                value = '0' * (10 - len(value)) + value
            temp = 0
            for i in range(9):
                temp += int(value[i]) * (10 - i)
            rem = temp % 11
            if (rem < 2 and int(value[9]) == rem) or (rem >= 2 and int(value[9]) == (11 - rem)):
                return value
            raise serializers.ValidationError("National Code is not valid.")
        raise serializers.ValidationError("National Code is not valid.")

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.get(username=self.context['request'].user.username)
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.save()
        instance.first_name_persian = validated_data['first_name_persian']
        instance.last_name_persian = validated_data['last_name_persian']
        instance.status = validated_data['status']
        instance.gender = validated_data['gender']
        instance.is_workshop_attender = validated_data['is_workshop_attender']
        instance.bio = validated_data['bio']
        instance.national_code = validated_data['national_code']
        instance.university = validated_data['university']
        instance.save()
        return instance


class GroupViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ('id', 'name', 'description', 'judge_password')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['members'] = MembershipViewSerializer(
            Membership.objects.filter(group=instance, status='A'), many=True).data
        return representation


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
        fields = ('id', 'challenger', 'group')

    def create(self, validated_data):
        membership = Membership.objects.filter(
            challenger=validated_data['challenger'], group=validated_data['group'])
        if membership.exists():
            if membership.filter(status='A').exists():
                raise serializers.ValidationError(
                    "You are already member of a group.")
            elif membership.filter(status='P').exists():
                raise serializers.ValidationError(
                    "You have already requested to join a group.")
            else:
                membership = membership.get()
                membership.status = 'P'
                membership.save()
        else:
            membership = Membership(
                challenger=validated_data['challenger'], group=validated_data['group'], role='M', status='P')
            membership.save()
        return membership
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['group'] = GroupViewSerializer(instance.group).data
        return representation


class MembershipViewSerializer(serializers.ModelSerializer):
    challenger = ChallengerSearchSerializer()

    class Meta:
        model = models.Membership
        fields = ('challenger', 'role', 'status')
