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

from .models import Post, Comment, Follow, LikePost, LikeComment
from .serializers import PostSerializer, CommentSerializer, UserSerializer, FollowSerializer, LikePostSerializer, LikeCommentSerializer

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
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
    def list(self, request, *args, **kwargs):
        if 'userIsgID' in request.query_params:
            userIsgID = request.query_params['userIsgID']
            uID_List = [int(userIsgID)]
            uID_List += [ queryset.following.id for queryset in Follow.objects.filter(user__id=userIsgID) ]

            queryset = self.filter_queryset(self.get_queryset()).filter(user__id__in = uID_List).order_by('-post_timestamp')
            posts = self.get_serializer(queryset, many=True)
            dataRespone = {'posts': posts.data}
            postID_List = [ data.id for data in queryset ]

            queryset = LikePost.objects.filter(post__id__in = postID_List)
            for p in dataRespone['posts']:
                p['likes'] = {'userID':[]}
                p['comments'] = []
                for qs in queryset:
                    if qs.post.id == p['id']:
                        p['likes']['userID'].append(qs.user.id)

            queryset = Comment.objects.filter(post__id__in = postID_List).order_by('-timestamp')
            self.serializer_class = CommentSerializer
            comments = self.get_serializer(queryset, many=True)
            CommentID_List = []
            for p in dataRespone['posts']:
                for c in comments.data:
                    if c['post'] == p['id']:
                        p['comments'].append(c)
                        CommentID_List.append(c['id'])

            queryset = LikeComment.objects.filter(comment__id__in = CommentID_List)
            for p in dataRespone['posts']:
                for c in p['comments']:
                    c['likes'] = {'userID':[]}
                    for qs in queryset:
                        if qs.comment.id == c['id']:
                            c['likes']['userID'].append(qs.user.id)

            
            # print(data2.data)
            return Response(dataRespone)
            # data = {"posts":serializer.data}
            
        else:
            queryset = self.filter_queryset(self.get_queryset())
        # # queryset = self.filter_queryset(self.get_queryset()).order_by('-post_timestamp')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
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
    