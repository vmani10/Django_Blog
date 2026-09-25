from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.text import slugify

from .models import Post, Category, Comment


# ============================================================
# HOME
# ============================================================

def home(request):

    posts = Post.objects.all().order_by("-created_at")
    categories = Category.objects.all()

    query = request.GET.get("q", "").strip()

    if query:
        posts = posts.filter(
            title__icontains=query
        )

    paginator = Paginator(posts, 6)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/home.html",
        {
            "posts": page_obj,
            "categories": categories,
            "query": query,
        }
    )


# ============================================================
# CATEGORY POSTS
# ============================================================

def category_posts(request, slug):

    category = get_object_or_404(
        Category,
        slug=slug
    )

    posts = Post.objects.filter(
        category=category
    ).order_by("-created_at")

    categories = Category.objects.all()

    paginator = Paginator(posts, 6)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/home.html",
        {
            "posts": page_obj,
            "categories": categories,
            "category": category,
        }
    )


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):

    posts = Post.objects.filter(
        author=request.user
    ).order_by("-created_at")

    comments = Comment.objects.filter(
        author=request.user
    )

    return render(
        request,
        "blog/dashboard.html",
        {
            "posts": posts,
            "comments": comments,
            "post_count": posts.count(),
            "comment_count": comments.count(),
        }
    )


# ============================================================
# POST DETAIL
# ============================================================

def post_detail(request, slug):

    post = get_object_or_404(
        Post,
        slug=slug
    )

    comments = Comment.objects.filter(
        post=post
    ).order_by("-created_at")

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comments": comments,
        }
    )


# ============================================================
# ADD COMMENT
# ============================================================

@login_required
def add_comment(request, slug):

    post = get_object_or_404(
        Post,
        slug=slug
    )

    if request.method == "POST":

        content = request.POST.get(
            "content",
            ""
        ).strip()

        if not content:

            messages.error(
                request,
                "Comment cannot be empty."
            )

            return redirect(
                "post_detail",
                slug=post.slug
            )

        Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )

        messages.success(
            request,
            "Comment added successfully!"
        )

    return redirect(
        "post_detail",
        slug=post.slug
    )


# ============================================================
# CREATE POST
# ============================================================

@login_required
def create_post(request):

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        content = request.POST.get(
            "content",
            ""
        ).strip()

        image = request.FILES.get("image")

        if not title:

            messages.error(
                request,
                "Post title is required."
            )

            return render(
                request,
                "blog/post_form.html"
            )

        if not content:

            messages.error(
                request,
                "Post content is required."
            )

            return render(
                request,
                "blog/post_form.html"
            )

        # Create unique slug

        base_slug = slugify(title)

        if not base_slug:
            base_slug = "post"

        slug = base_slug

        counter = 1

        while Post.objects.filter(
            slug=slug
        ).exists():

            slug = f"{base_slug}-{counter}"

            counter += 1

        Post.objects.create(
            title=title,
            slug=slug,
            content=content,
            image=image,
            author=request.user
        )

        messages.success(
            request,
            "Post created successfully!"
        )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "blog/post_form.html"
    )


# ============================================================
# EDIT POST
# ============================================================

@login_required
def edit_post(request, slug):

    post = get_object_or_404(
        Post,
        slug=slug
    )

    # Only the author can edit

    if post.author != request.user:

        messages.error(
            request,
            "You are not allowed to edit this post."
        )

        return redirect(
            "dashboard"
        )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        content = request.POST.get(
            "content",
            ""
        ).strip()

        image = request.FILES.get("image")

        if not title:

            messages.error(
                request,
                "Post title is required."
            )

            return render(
                request,
                "blog/edit_post.html",
                {
                    "post": post
                }
            )

        if not content:

            messages.error(
                request,
                "Post content is required."
            )

            return render(
                request,
                "blog/edit_post.html",
                {
                    "post": post
                }
            )

        post.title = title
        post.content = content

        if image:
            post.image = image

        # Keep the existing slug.
        # This keeps existing links working.

        post.save()

        messages.success(
            request,
            "Post updated successfully!"
        )

        return redirect(
            "post_detail",
            slug=post.slug
        )

    return render(
        request,
        "blog/edit_post.html",
        {
            "post": post
        }
    )


# ============================================================
# DELETE POST
# ============================================================

@login_required
def delete_post(request, slug):

    post = get_object_or_404(
        Post,
        slug=slug
    )

    if post.author != request.user:

        messages.error(
            request,
            "You are not allowed to delete this post."
        )

        return redirect(
            "dashboard"
        )

    if request.method == "POST":

        post.delete()

        messages.success(
            request,
            "Post deleted successfully!"
        )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "blog/delete_post.html",
        {
            "post": post
        }
    )


# ============================================================
# REGISTER
# ============================================================

def register(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not username:

            return render(
                request,
                "blog/register.html",
                {
                    "error": "Username is required."
                }
            )

        if not password:

            return render(
                request,
                "blog/register.html",
                {
                    "error": "Password is required."
                }
            )

        if password != confirm_password:

            return render(
                request,
                "blog/register.html",
                {
                    "error": "Passwords do not match."
                }
            )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "blog/register.html",
                {
                    "error": "Username already exists."
                }
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(
            request,
            user
        )

        messages.success(
            request,
            "Account created successfully!"
        )

        return redirect(
            "home"
        )

    return render(
        request,
        "blog/register.html"
    )


# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            messages.success(
                request,
                "Login successful!"
            )

            return redirect(
                "home"
            )

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "blog/login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect(
        "home"
    )


# ============================================================
# PROFILE
# ============================================================

@login_required
def profile(request):

    # IMPORTANT:
    # We do NOT use request.user.profile.
    # This prevents:
    # "User has no profile."

    posts = Post.objects.filter(
        author=request.user
    ).order_by("-created_at")

    return render(
        request,
        "blog/profile.html",
        {
            "user": request.user,
            "posts": posts,
            "post_count": posts.count(),
        }
    )