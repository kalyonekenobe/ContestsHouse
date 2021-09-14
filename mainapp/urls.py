from django.urls import path
from .views import *

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('startups/', StartupListView.as_view(), name='startup_list'),
    path('posts/', PostListView.as_view(), name='post_list'),
    path('startups/<str:slug>/', StartupDetailView.as_view(), name='startup_detail'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('startups/follow/<str:slug>/', FollowStartupView.as_view(), name='follow_startup'),
    path('startups/page/<int:page>/', StartupListView.as_view(), name='startup_list'),
    path('startups/<str:slug>/comment/create', CreateCommentView.as_view(), name='create_comment'),
]
