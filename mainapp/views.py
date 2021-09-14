import json, base64
from django.db import transaction
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import DetailView, View
from django.http import HttpResponseRedirect, HttpResponse
from .forms import *
from .utils import *


class BaseView(View):
    
    def get(self, request, *args, **kwargs):
        startup_list = Startup.objects.all().order_by('-datetime')[:6]
        context = {
            'startups': startup_list,
            'page': 1,
        }
        return render(request, 'base.html', context)


class StartupListView(View):
    
    STARTUPS_ON_PAGE = 9
    
    def get(self, request, *args, **kwargs):
        startup_list = Startup.objects.all().order_by('-datetime')
        page = 1 if not kwargs.get('page') else kwargs.get('page')
        paginator = Paginator(startup_list, self.STARTUPS_ON_PAGE)
        startup_list_by_page = paginator.get_page(page)
        context = {
            'startups': startup_list_by_page,
            'page': page,
            'pages_number': paginator.page_range,
        }
        return render(request, 'startups.html', context)
    

class PostListView(View):
    
    def get(self, request, *args, **kwargs):
        post_list = Post.objects.all().order_by('-datetime')
        context = {
            'posts': post_list,
        }
        return render(request, 'posts.html', context)
    

class StartupDetailView(DetailView):
    
    model = Startup
    queryset = Startup.objects.all()
    context_object_name = 'startup'
    template_name = 'startup_detail.html'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm({'author': self.request.user.username})
        return context
    

class PostDetailView(DetailView):
    
    model = Post
    queryset = Post.objects.all()
    context_object_name = 'post'
    template_name = 'post_detail.html'
    pk_url_kwarg = 'id'


class FollowStartupView(View):
    
    def post(self, request, *args, **kwargs):
        user = request.user
        startup = Startup.objects.get(slug=kwargs.get('slug'))
        if user not in startup.followers.all():
            startup.followers.add(user)
            http_response = 'follow'
        else:
            startup.followers.remove(user)
            http_response = 'unfollow'
        startup.save()
        data = {
            'action': http_response,
            'followers_quantity': startup.followers.count(),
        }
        return HttpResponse(json.dumps(data))
    
    
class CreateCommentView(View):
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        startup = Startup.objects.get(slug=kwargs.get('slug'))
        http_response = 201
        data = json.loads(request.body)
        data['reply_to'] = base64.b64decode(data['reply_to'].encode('ascii')).decode('ascii')
        form = CommentForm(data or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.username = form.cleaned_data['author']
            comment.text = form.cleaned_data['text']
            comment.user_ip = get_client_ip(request)
            attached_files = data['attached_files']
            for attached_file in attached_files:
                file = File.objects.create(attached_file.name, attached_file)
                comment.attached_files.add(file)
            comment.save()
            if data['reply_to']:
                comment_parent = Comment.objects.get(id=data['reply_to'])
                if comment_parent:
                    comment_parent.children.add(comment)
                    comment_parent.save()
            startup.comments.add(comment)
            startup.save()
        else:
            http_response = 406
        return HttpResponse(json.dumps(http_response))
    