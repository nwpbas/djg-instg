from django.contrib import admin

# Register your models here.
from .models import Post, Comment, Follow, LikePost, LikeComment, Profile

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(LikePost)
admin.site.register(LikeComment)
admin.site.register(Profile)