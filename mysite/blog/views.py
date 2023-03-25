from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from .models import Post
from .forms import EmailPostForm, CommentForm

from taggit.models import Tag


def post_share(request, post_id):
    # Retrieve by post id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == "POST":
        # Form submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # ... send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url} " f"{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    template = 'blog/post/share.html'
    context = {
        'post': post,
        'form': form,
        'sent': sent,
    }
    return render(request, template, context)


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    template = 'blog/post/list.html'
    context = {'page': page, 'posts': posts, 'tag': tag}
    return render(request, template, context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post, 
        slug=post, 
        status='published', 
        publish__year=year, 
        publish__month=month, 
        publish__day=day
        )
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        #  A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Creeate comment obhect but not save
            new_comment = comment_form.save(commit=False)
            # Assign to current post
            new_comment.post = post
            # save the comment
            new_comment.save()
    else:
        comment_form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')).order_by(
            '-same_tags', '-publish')[:4]
    template = 'blog/post/detail.html'
    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts
    }
    return render(request, template, context)
