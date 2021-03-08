from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer, GroupSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from .bin import delete, get, add, update, list_all_keys, find_substr, get_dict, exist


class FindApiView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        seeked = request.query_params.get('seeked')
        if seeked:
            res = find_substr(seeked)
            content = {
                'keys': ["http://127.0.0.1:8000/api/dict?key=%s" % x for x in res]
            }
            return Response(content)
        else:
            return Response({'status': 'error','reason': 'wrong data'}, status=404)


class DictApiView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status = 200
        key = request.query_params.get('key')
        if key:
            try:
                value = get(key)
                content = {
                    'key': key,
                    'value': value
                }
            except:
                content = {
                    'status': 'error',
                    'reason': 'no such key'
                }
                status = 404
        else:
            file = get_dict()
            for x in file:
                file[x] = "http://127.0.0.1:8000/api/dict?key=%s" % x
            content = {
                'file': file
            }
        return Response(content, status=status)

    def post(self, request):
        key, value = request.data.get('key'), request.data.get('value')
        if not request.user.groups.filter(name='admin').exists():
            content = {'status': 'error',
                       'reason': 'u must be in admin group'}
        elif exist(key):
            content = {'status': 'error',
                       'reason': 'key already exist'}
        else:
            add(key, value)
            content = {
                'key': key,
                'value': value
            }
        return Response(content)

    def delete(self, request):
        status = 200
        if request.user.groups.filter(name='admin').exists():
            key = request.query_params.get('key')
            try:
                value = delete(key)
                content = {
                    'key': key,
                    'value': value,
                }
            except Exception as e:
                content = {'status': 'error',
                           'reason': e.__str__()}
                status = 404
        else:
            content = {'status': 'error',
                       'reason': 'u must be in admin group'}
            status = 404
        return Response(content, status=status)

    def put(self, request):
        status = 200
        key, value = request.data.get('key'), request.data.get('value')
        if not request.user.groups.filter(name='admin').exists():
            content = {'status': 'error',
                       'reason': 'u must be in admin group'}
            status = 400
        elif key and value:
            try:
                old_value = update(key, value)
                content = {
                    'key': key,
                    'old_value': old_value,
                    'new_value': value
                }
            except Exception as e:
                content = {'status': 'error',
                           'reason': 'key doesnt exist'}
                status = 400
        else:
            content = {'status': 'error',
                       'reason': 'no key or value'}
            status = 400
        return Response(content, status=status)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
