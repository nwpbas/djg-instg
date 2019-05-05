from .models import Post, Comment, Follow, LikePost, LikeComment
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id','user','caption', 'image')
        # extra_kwargs = {'user' : {'required': True}}

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id','user','post','text')

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

class UserSerializer(serializers.HyperlinkedModelSerializer):
    # username = serializers.CharField(
    #     max_length=32,
    #     validators=[UniqueValidator(queryset=User.objects.all())]
    #     )
        
    # email = serializers.EmailField(
    #     required=False,
    #     validators=[UniqueValidator(queryset=User.objects.all())]
    #     )

    # password = serializers.CharField(min_length=8, write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'username' : {'write_only': True},
            'password' : {'min_length':8,'write_only': True, 'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user
    # def create(self, validated_data):
    #     # raise_errors_on_nested_writes('create', self, validated_data)
    #     ModelClass = self.Meta.model
    #     info = model_meta.get_field_info(ModelClass)
    #     many_to_many = {}
    #     for field_name, relation_info in info.relations.items():
    #         if relation_info.to_many and (field_name in validated_data):
    #             many_to_many[field_name] = validated_data.pop(field_name)
        
    #     try:
    #         instance = ModelClass._default_manager.create_user(**validated_data)
    #     except TypeError:
    #         tb = traceback.format_exe()
    #         msg = ()