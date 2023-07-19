from rest_framework.response import Response
from accounts.serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, \
    UserChangePasswordSerializer
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from .renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import json
import time
import random
import datetime

# Primetheus
from prometheus_client import Gauge  # Counter, Histogram, Summary,

# REQUESTS = Counter('external_call_requests_total', 'Total number of requests to third party API')
# LATENCY_PROVIDER = Histogram('provider_latency_ms', 'Provider Response Time in ms', ['providers','response_code'],buckets=[0, 50, 200, 400, 800, 1600, 3200])
# LATENCY_PROVIDER = Histogram('provider_latency_ms', 'Provider Response Time in ms', ['providers'],buckets=[0, 50, 200, 400, 800, 1600, 3200])
# PROVIDER_LATENCY_SUMMARY = Summary('provider_response_latency_milliseconds', 'Response latency in ms',['providers'])
connection_gauge = Gauge('number_of_in_progress_requests', "hello")  # 'Description of gauge'


# Generate token manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# @connection_gauge.track_inprogress()
def homePageView(request):
    return HttpResponse("Hello, World!")


class Test(APIView):
    @connection_gauge.track_inprogress()
    def post(self, request):
        body = json.loads(request.body.decode('utf-8'))
        print(body)
        # content = body['content']
        req_id = random.randint(1000, 9999)
        print(f"received the request with req_id : {req_id} time {datetime.datetime.now()} content {body}, going to sleep for 10s ")
        time.sleep(10)
        print(f"Completed sleep for request with req_id : {req_id} time {datetime.datetime.now()} ")

        return HttpResponse(body)


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'User got registered successfully!'},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                            status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": "User successfully logged out."}, status=status.HTTP_200_OK)
