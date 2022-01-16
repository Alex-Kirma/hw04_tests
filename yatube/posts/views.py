from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from yatube.settings import VAR_NUMBER_POSTS

from .models import Group, Post
from .forms import PostForm


def paginator_page(request, posts):
    paginator = Paginator(posts, VAR_NUMBER_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.all()
    page_obj = paginator_page(request, posts)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator_page(request, posts)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    number_of_posts = posts.count()
    page_obj = paginator_page(request, posts)
    context = {
        "page_obj": page_obj,
        "author": author,
        "number_of_posts": number_of_posts,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    posts = get_object_or_404(Post, pk=post_id)
    number_of_posts = posts.author.posts.count()
    context = {
        "post": posts,
        "number_of_posts": number_of_posts,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=request.user)

    groups = Group.objects.all()
    context = {
        "form": form,
        "groups": groups,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    groups = Group.objects.all()
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post.pk)
    if form.is_valid():
        post = form.save()
        return redirect("posts:post_detail", post_id=post.pk)
    context = {
        "groups": groups,
        "is_edit": True,
        "post": post,
        "form": form,
    }
    return render(request, "posts/create_post.html", context)
