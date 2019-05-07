from .models import Post, Comment, Follow, LikePost, LikeComment, Profile
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
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
        fields = ('id', 'username', 'email', 'password', 'my_profile')
        extra_kwargs = {
            'password' : {'min_length':8, 'write_only': True, 'required': True},
            'my_profile' : {'read_only': True},
        }

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.save()
        user.set_password(validated_data['password'])
        user.save()
        Profile.objects.create(user=user)
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

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id','user','photo','bio','website')
        # extra_kwargs = {
        #     'photo' : {'read_only': True},
        # }
    


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
    user = UserSerializer()
    likecomment_relate = LikeCommentSerializer(many=True,read_only=True)
    class Meta:
        model = Comment
        fields = ('id','user','post','text','likecomment_relate')
        extra_kwargs = {
                # 'post' : {'write_only': True},
                }

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments_relate = CommentSerializer(many=True,read_only=True)
    likepost_relate = LikePostSerializer(many=True,read_only=True)
    class Meta:
        model = Post
        fields = ('id','user','caption', 'image', 'post_timestamp', 'caption_timestamp', 'comments_relate', 'likepost_relate')
        # extra_kwargs = {
        #         'caption' : {'required': True},
        #         }

    # def create(self, validated_data):
        # print(validated_data)
        # user = User.objects.get(pk=validated_data[])
        # user.save()
        # user.set_password(validated_data['password'])
        # user.save()
        # Profile.objects.create(user=user)
        # return user
