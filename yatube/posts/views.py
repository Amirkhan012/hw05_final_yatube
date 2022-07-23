from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from .models import Follow, User
from .models import Group, Post
from .forms import PostForm, CommentForm
from posts.utils import paginate

PAGINATE_BY = 10


@cache_page(20, cache='default', key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginate(request, post_list)
    context = {
        'index': True,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginate(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    following = (
        user.is_authenticated
        and user != author
        and Follow.objects.filter(
            author=author).filter(user=user).exists()
    )
    post_list = author.posts.all()
    count = author.posts.all().count()
    page_obj = paginate(request, post_list)
    context = {
        'author': author,
        'following': following,
        'page_obj': page_obj,
        'count': count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comment_list = post.comments.all()
    context = {
        'post': post,
        'comments': comment_list,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required(login_url='/auth/login/')
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", request.user.username)
    return render(request, 'posts/create_post.html', {'form': form, })


@login_required(login_url='/auth/login/')
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.delete()
    return redirect("posts:profile", request.user.username)


@login_required(login_url='/auth/login/')
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user
    )
    page_obj = paginate(request, post_list)
    context = {
        'follow': True,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user.is_authenticated:
        if user != author:
            Follow.objects.get_or_create(
                user=user,
                author=author,
            )
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    user = request.user
    get_object_or_404(
        Follow,
        user=user,
        author__username=username,
    ).delete()
    return redirect('posts:profile', username=username)
