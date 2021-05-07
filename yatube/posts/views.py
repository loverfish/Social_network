from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment
from .utils import post_paginator


def index(request):
    post_list = Post.objects.order_by('-pub_date').all() # noqa
    page, paginator = post_paginator(request, post_list)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date').all() # noqa
    page, paginator = post_paginator(request, posts, 5)
    return render(request, 'posts/group.html', {'group': group, 'page': page, 'paginator': paginator})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).order_by('-pub_date').all() # noqa
    page, paginator = post_paginator(request, posts, 5)
    context = {
        'page': page,
        'paginator': paginator,
        'author': author,
        'posts_count': len(posts),
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    comment_list = Comment.objects.order_by('-created').filter(post=post_id)
    post = get_object_or_404(Post, pk=post_id)
    posts = Post.objects.filter(author=author).all() # noqa
    return render(request, 'posts/post.html', {
        'post': post,
        'author': author,
        'posts_count': len(posts),
        'comment_list': comment_list,
    })


@login_required()
def new_post(request):
    bound_form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if bound_form.is_valid():
            post = bound_form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        # return render(request, 'posts/new_post.html', {'form': bound_form})
    # form = PostForm
    return render(request, 'posts/new_post.html', {'form': bound_form})


@login_required()
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        bound_form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
        if request.method == 'POST':
            if bound_form.is_valid():
                bound_form.save()
                return redirect('post', username=post.author, post_id=post.id)
        return render(request, 'posts/new_post.html', {'form': bound_form, 'post': 1})
    return redirect('post', username=username, post_id=post_id)


@login_required()
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).all()
    post = get_object_or_404(Post, id=post_id)
    comment_list = Comment.objects.order_by('-created').filter(post=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('index')
    return render(request, 'posts/post.html', {
        'form': form,
        'post': post,
        'comment_list': comment_list,
        'posts_count': len(posts),
        'author': author,
    })


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
