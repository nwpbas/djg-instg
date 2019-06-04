"""data_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
from instagram_server import views
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'follows', views.FollowViewSet)
router.register(r'likeposts', views.LikePostViewSet)
router.register(r'likecomments', views.LikeCommentViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.ProfileViewSet)
# for i in router.urls:
#     print(i,i.__dict__)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/token-auth/', views.CustomAuthToken.as_view()),
    path('api/api-token-auth/', obtain_auth_token)
    # path('instagram/', include('instagram_server.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
