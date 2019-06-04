from .models import Post, Comment, Follow, LikePost, LikeComment, Profile
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'email', 'password', 'my_profile')
        extra_kwargs = {
            'username' : {'min_length':6, },
            'password' : {'min_length':8, 'write_only': True},
            'my_profile' : {'read_only': True}
        }
    
    # def create(self, validated_data):
    #     profile_data = {
    #         'photo':validated_data.pop('photo'),
    #         'bio':validated_data.pop('bio'),
    #         'website':validated_data.pop('website'),}
    #     user = User.objects.create(**validated_data)
    #     Profile.objects.create(user=user, **profile_data)
    #     return user
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.save()
        user.set_password(password)
        user.save()
        # Profile.objects.create(user=user)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id','user','photo','bio','website')
        extra_kwargs = {
            # 'user' : { 'many': False, }
        }

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('id','user','following')

class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikePost
        fields = ('id','user','post')

class LikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeComment
        fields = ('id','user','comment')

class CommentSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    likecomment_relate = LikeCommentSerializer(many=True, read_only=True)
    class Meta:
        model = Comment
        fields = ('id','user','post','text','timestamp','likecomment_relate')
        # extra_kwargs = {
        #         # 'post' : {'write_only': True},
        #         }

class PostSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    comments_relate = CommentSerializer(many=True, read_only=True)
    likepost_relate = LikePostSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ('id','user','caption', 'image', 'post_timestamp', 'caption_timestamp', 'comments_relate', 'likepost_relate')

