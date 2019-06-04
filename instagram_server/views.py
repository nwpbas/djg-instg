from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpRequest
from django.contrib.auth.models import User

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers
from django.forms.models import model_to_dict
import datetime
import json
import copy

from .models import Post, Comment, Follow, LikePost, LikeComment, Profile
from .serializers import PostSerializer, CommentSerializer, UserSerializer, FollowSerializer, LikePostSerializer, LikeCommentSerializer, ProfileSerializer

class CustomAuthToken(ObtainAuthToken):
    queryset = Token.objects.all()
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        profile_id = Profile.objects.get(user=user).id
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user_id': user.id,
            'profile_id':profile_id,
            'token': token.key,
        })

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-post_timestamp")
    serializer_class = PostSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    # def create(self, request, *args, **kwargs):
    #     data = request.data
    #     print(data)
    #     # print(request.headers)
    #     # for k in request.META:
    #     #     print("{} : {}".format(k, request.META[k]))
    #     user_obj = User.objects.get(pk=data['user'])
    #     post = Post.objects.create(user=user_obj, caption=data['caption'], image=data['image'])
    #     # print(post.__dict__)
    #     data_response = model_to_dict(post)
    #     # data_response['caption_timestamp'] = post.__dict__['caption_timestamp'].__str__()
    #     data_response['caption_timestamp'] = post.caption_timestamp.__str__()
    #     # data_response['post_timestamp'] = post.__dict__['post_timestamp'].__str__()
    #     data_response['post_timestamp'] = post.post_timestamp.__str__()
    #     data_response['image'] = "http://{}/media/{}".format(request.get_host(), data_response['image'].name)
    #     return Response(data_response, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        # for i in Profile.objects.filter(id = 11):
        #     print(model_to_dict(i))
        # for i in output_dict:
        #     print(i)
        new_request = HttpRequest()
        new_request.method = 'GET'
        # new_request.META['SERVER_NAME'] = request.META['REMOTE_ADDR']
        new_request.META['SERVER_NAME'] = request.get_host().split(":")[0]
        new_request.META['SERVER_PORT'] = request.META['SERVER_PORT']
        # for i in request.META:
        #     print(i, request.META[i])
        users = {}
        profiles = {}
        for user in json.loads(json.dumps(UserViewSet.as_view({'get': 'list'})(new_request).data)):
            users[user['id']] = user
        for prf in json.loads(json.dumps(ProfileViewSet.as_view({'get': 'list'})(new_request).data)):
            profiles[prf['id']] = prf
        
        for _id in users:
            if len(users[_id]['my_profile']) > 0:
                id_prof = users[_id]['my_profile'][0]
                users[_id]['my_profile'] = profiles[id_prof]
            # print(users[_id])

        for post in serializer.data:
            id_user = post['user']
            post['user'] = users[id_user]
            for cmt in post['comments_relate']:
                id_user = cmt['user']
                cmt['user'] = users[id_user]

            # pr_fl =  model_to_dict(Profile.objects.filter(id = id_prof)[0])
            # if pr_fl['photo']:
            #     pr_fl['photo'] = "http://{}/media/{}".format(request.get_host(), pr_fl['photo'].name)
            # else:
            #     pr_fl['photo'] = ""
            # post['user']['my_profile'] = pr_fl

        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("post_timestamp")
    serializer_class = CommentSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    # def create(self, request, *args, **kwargs):
    #     data = request.data
    #     user_obj = User.objects.get(pk=data['user_id'])
    #     post_obj = Post.objects.get(pk=data['post_id'])
    #     comment = Comment.objects.create(user=user_obj, post=post_obj, text=data['comment'])
    #     data_response = model_to_dict(comment)
    #     data_response['timestamp'] = comment.timestamp.__str__()
    #     return Response(data_response)

    def create(self, request, *args, **kwargs):
        # data = request.data
        # print(data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # print(serializer.data)

        # for i in request.META : 
        #     print (i, request.META[i])
        new_request = HttpRequest()
        new_request.method = 'GET'
        # new_request.META['SERVER_NAME'] = request.META['REMOTE_ADDR']
        new_request.META['SERVER_NAME'] = request.get_host().split(":")[0]
        new_request.META['SERVER_PORT'] = request.META['SERVER_PORT']
        
        user = UserViewSet.as_view({'get': 'retrieve'})(new_request, pk=request.data['user']).data
        profile = ProfileViewSet.as_view({'get': 'retrieve'})(new_request, pk=user['my_profile'][0]).data
        # profile = ProfileViewSet.as_view({'get': 'retrieve'})(new_request, pk=user['my_profile'][0]).data.render().content
        # data = UserViewSet.as_view({'get': 'list'})(new_request).data
        # output_dict = json.loads(json.dumps(data))
        # for i in output_dict:
        #     print(i)

        data_respone = dict(serializer.data)
        data_respone['user'] = user
        data_respone['user']['my_profile'] = profile

        headers = self.get_success_headers(serializer.data)
        return Response(data_respone, status=status.HTTP_201_CREATED, headers=headers)
        # return Response()

    # def list(self, request, *args, **kwargs):
    #     if 'commentID' in request.query_params:
    #         cmID_list = map(int, request.query_params['commentID'].split(','))
    #         queryset = Comment.objects.filter(pk__in = cmID_list)
    #     else:
    #         queryset = self.filter_queryset(self.get_queryset())
    #     # page = self.paginate_queryset(queryset)
    #     # if page is not None:
    #     #     print("Page not None")
    #     #     serializer = self.get_serializer(page, many=True)
    #     #     return self.get_paginated_response(serializer.data)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        # data = dict(request.data)
        # data = { key:value[0] for key, value in data.items()}
        # print(data)
        # if data.get('photo') == '':
            # data.pop('photo')
        # user = User(username=data.pop('username'))
        # user.save()
        # user.set_password(data.pop('password'))
        # user.save()
        # profile = Profile.objects.create(user=user, **data)
        # data_response = model_to_dict(user)
        # print(data_response)
        # data_response.update(model_to_dict(profile))
        # print()
        # print(data_response)
        # return Response()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        data = { key:request.data[key] for key in request.data if key not in ['username','password']}
        Profile.objects.create(user=User.objects.get(pk=serializer.data['id']), **data)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # serializer = UserSerializer(data=request.data)
        # if serializer.is_valid():
        #     user = serializer.save()
        #     if user:
        #         json = serializer.data
        #         json['token'] = token.key
        #         return Response(json, status=status.HTTP_201_CREATED)

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())

    #     # page = self.paginate_queryset(queryset)
    #     # if page is not None:
    #     #     serializer = self.get_serializer(page, many=True)
    #     #     return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     # for i in Profile.objects.filter(id = 11):
    #     #     print(model_to_dict(i))
    #     for us in serializer.data:
    #         id_prof = us['my_profile'][0]
    #         pr_fl =  model_to_dict(Profile.objects.filter(id = id_prof)[0])
    #         if pr_fl['photo']:
    #             pr_fl['photo'] = "http://{}/media/{}".format(request.get_host(), pr_fl['photo'].name)
    #         else:
    #             pr_fl['photo'] = ""
    #         us['my_profile'] = pr_fl
    #         # print(us)
    #     return Response(serializer.data)

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

class LikePostViewSet(viewsets.ModelViewSet):
    queryset = LikePost.objects.all()
    serializer_class = LikePostSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

class LikeCommentViewSet(viewsets.ModelViewSet):
    queryset = LikeComment.objects.all()
    serializer_class = LikeCommentSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        new_request = HttpRequest()
        new_request.method = 'GET'
        # new_request.META['SERVER_NAME'] = request.META['REMOTE_ADDR']
        new_request.META['SERVER_NAME'] = request.get_host().split(":")[0]
        new_request.META['SERVER_PORT'] = request.META['SERVER_PORT']
        
        user = json.loads(json.dumps(UserViewSet.as_view({'get': 'retrieve'})(new_request, pk=serializer.data['user']).data))
        data_respone = dict(serializer.data)
        data_respone['user'] = user

        return Response(data_respone)
    