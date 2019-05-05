from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    following = models.ForeignKey(User, related_name='user_following', on_delete=models.CASCADE, default=None)

def img_post_location(instance, filename):
    return "images/posts/userID-{0}/userID-{0}-postID-{1}".format(instance.user.id, filename)

def img_profile_location(instance, filename):
    return "images/profile/userID-{0}/userID-{0}-profileID-{1}".format(instance.user.id, filename)

class Profile(models.Model):
    user = models.ForeignKey(User, related_name='user_profile', on_delete=models.CASCADE, default=None)
    photo = models.ImageField(upload_to = img_profile_location, blank = True, null = True )
    bio = models.TextField(blank = True, null = True)
    website = models.URLField(blank = True, null = True)

class Post(models.Model):
    user = models.ForeignKey(User, related_name='post_user', on_delete=models.CASCADE, default=None)
    caption = models.TextField(blank = True, null = True)
    post_timestamp = models.DateTimeField(auto_now_add=True)
    caption_timestamp = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to = img_post_location)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

class LikePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class LikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)