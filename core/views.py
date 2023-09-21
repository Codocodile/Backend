from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Challenger
from core.serializers import ChallengerSerializer, GroupSerializer


# Create your views here.
@api_view(['Get', 'Post', 'Put'])
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


class ChallengerCreateAPIView(APIView):
    def post(self, request):
        serializer = ChallengerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamCreateAPIView(APIView):
    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
