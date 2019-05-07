from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
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

from .models import Post, Comment, Follow, LikePost, LikeComment, Profile
from .serializers import PostSerializer, CommentSerializer, UserSerializer, FollowSerializer, LikePostSerializer, LikeCommentSerializer, ProfileSerializer

class CustomAuthToken(ObtainAuthToken):
    queryset = Token.objects.all()
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        print(user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user_id': user.id,
            'token': token.key,
        })

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-post_timestamp")
    serializer_class = PostSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data
        # print(request.headers)
        # for k in request.META:
        #     print("{} : {}".format(k, request.META[k]))

        post = Post.objects.create(user=User.objects.get(
            pk=data['user'])
            , caption=data['caption']
            , image=data['image'])
        # print(post.__dict__)
        # print(post.__dict__['image'])
        # print(post.__dict__['caption_timestamp'].__str__())
        # print(post.__dict__['caption_timestamp'].ctime())
        data_response = model_to_dict(post)
        data_response['caption_timestamp'] = post.__dict__['caption_timestamp'].__str__()
        data_response['post_timestamp'] = post.__dict__['post_timestamp'].__str__()
        data_response['image'] = "http://{}/media/{}".format(request.get_host(), post.__dict__['image'])
        # return Response(data_response, status=status.HTTP_201_CREATED)
        # return Response(model_to_dict(post), status=status.HTTP_201_CREATED)
        return Response()
    
    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     posts = self.get_serializer(queryset, many=True)
    #     dataRespone = {'posts': posts.data}

    #     # self.serializer_class = LikePostSerializer
    #     # likes_post = self.get_serializer(LikePost.objects.all(), many=True)
    #     likes_post = LikePost.objects.all()

    #     self.serializer_class = CommentSerializer
    #     comments = self.get_serializer(Comment.objects.all(), many=True)
    #     # comments = Comment.objects.all()

    #     # self.serializer_class = LikeCommentSerializer
    #     # likes_cmmt = self.get_serializer(LikeComment.objects.all(), many=True)
    #     likes_cmmt = LikeComment.objects.all()

    #     for p in dataRespone['posts']:
    #         p['likes'] = {'userID':[]}
    #         p['comments'] = []
    #         for lks in likes_post:
    #             if lks.post.id == p['id']:
    #                 p['likes']['userID'].append(lks.user.id)
    #                 # del likes_post[lks.id]

    #         for cmt in comments.data:
    #             if cmt['post'] == p['id']:
    #                 p['comments'].append(cmt)
    #                 #  del comments[cmt['id']]

    #         for c in p['comments']:
    #             c['likes'] = {'userID':[]}
    #             for lkc in likes_cmmt:
    #                 if lkc.comment.id == c['id']:
    #                     c['likes']['userID'].append(lkc.user.id)
    #                     # del likes_cmmt[lkc.id]

    #     return Response(dataRespone)

    #     if 'userIsgID' in request.query_params:
    #         print("request.query_params['userIsgID'] : ",request.query_params['userIsgID'])
    #         userIsgID = request.query_params['userIsgID']
    #         uID_List = [int(userIsgID)]
    #         uID_List += [ queryset.following.id for queryset in Follow.objects.filter(user__id=userIsgID) ]

    #         queryset = self.filter_queryset(self.get_queryset()).filter(user__id__in = uID_List).order_by('-post_timestamp')
    #         posts = self.get_serializer(queryset, many=True)
    #         dataRespone = {'posts': posts.data}
    #         postID_List = [ data.id for data in queryset ]

    #         queryset = LikePost.objects.filter(post__id__in = postID_List)
    #         for p in dataRespone['posts']:
    #             p['likes'] = {'userID':[]}
    #             p['comments'] = []
    #             for qs in queryset:
    #                 if qs.post.id == p['id']:
    #                     p['likes']['userID'].append(qs.user.id)

    #         queryset = Comment.objects.filter(post__id__in = postID_List).order_by('-timestamp')
    #         self.serializer_class = CommentSerializer
    #         comments = self.get_serializer(queryset, many=True)
    #         CommentID_List = []
    #         for p in dataRespone['posts']:
    #             for c in comments.data:
    #                 if c['post'] == p['id']:
    #                     p['comments'].append(c)
    #                     CommentID_List.append(c['id'])

    #         queryset = LikeComment.objects.filter(comment__id__in = CommentID_List)
    #         for p in dataRespone['posts']:
    #             for c in p['comments']:
    #                 c['likes'] = {'userID':[]}
    #                 for qs in queryset:
    #                     if qs.comment.id == c['id']:
    #                         c['likes']['userID'].append(qs.user.id)

            
    #         # print(data2.data)
    #         return Response(dataRespone)
    #         # data = {"posts":serializer.data}
            
    #     else:
    #         queryset = self.filter_queryset(self.get_queryset())
    #     # # queryset = self.filter_queryset(self.get_queryset()).order_by('-post_timestamp')
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data
        comment = Comment.objects.create(
            user=User.objects.get(pk=data['user_id'])
            , post=Post.objects.get(pk=data['post_id'])
            , text=data['comment'])
        data_response = model_to_dict(comment)
        data_response['timestamp'] = comment.__dict__['timestamp'].__str__()
        # data_response['caption_timestamp'] = post.__dict__['caption_timestamp'].__str__()
        # data_response['post_timestamp'] = post.__dict__['post_timestamp'].__str__()
        # data_response['image'] = "http://{}/media/{}".format(request.get_host(), post.__dict__['image'])
        # return Response(data_response, status=status.HTTP_201_CREATED)
        # return Response(model_to_dict(post), status=status.HTTP_201_CREATED)
        return Response(data_response)

    # def create(self, request, *args, **kwargs):
    #     print(request.data)
    #     return Response()
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        if 'commentID' in request.query_params:
            cmID_list = map(int, request.query_params['commentID'].split(','))
            queryset = Comment.objects.filter(pk__in = cmID_list)
        else:
            queryset = self.filter_queryset(self.get_queryset())
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     print("Page not None")
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # serializer = UserSerializer(data=request.data)
        # if serializer.is_valid():
        #     user = serializer.save()
        #     if user:
        #         json = serializer.data
        #         json['token'] = token.key
        #         return Response(json, status=status.HTTP_201_CREATED)

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    
@csrf_exempt
def index(request):
    print('-------------Receive File---------------')
    post_obj = Post.objects.create(amount_like=0, image=request.FILES['photo'])
    # if (request.FILES['photo'].multiple_chunks()):
    #     storage = FileSystemStorage(
    #                 location = settings.MEDIA_ROOT, 
    #                 base_url = settings.MEDIA_URL,
    #               )
    #     content = request.FILES['photo']
    #     print(type(content))
    #     name = storage.save('testPic', content=content)
    #     print( storage.url(name) )

    print(request.FILES['photo'].name)
    print(request.FILES['photo'].content_type)
    print(request.FILES['photo'].size / 1024)
    return JsonResponse({'image_path': post_obj.image.url})
    