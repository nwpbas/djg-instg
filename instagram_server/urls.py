from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('upload-pic/', views.index),
    # path('<int:number_m>/', views.multi_tb, name='multi_tb'),

    # # ex: /polls/5/
    # path('<int:question_id>/', views.detail, name='detail'),
]