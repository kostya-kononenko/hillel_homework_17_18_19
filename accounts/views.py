from django.shortcuts import render
from .forms import UserCreationForm, ContactFrom
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from .models import Post, Comment, User
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .tasks import send_mail as celery_send_mail
from .tasks import send_mail_to_user, send_mail_comment, send_mail_contact
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string


def contact_form(request):
    data = dict()
    if request.method == "POST":
        form = ContactFrom(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            send_mail_contact.delay(subject, message, from_email)
            msg = ['Congratulations. Message sent !!!']
            data['html_contact_msg'] = render_to_string('base_2.html', {'messages': msg})
            data['form_is_valid'] = True

    else:
        form = ContactFrom()
        data['form_is_valid'] = False

    context = {'form': form}
    data['html_form'] = render_to_string('modal.html', context, request=request)

    return JsonResponse(data)


class Register(FormView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)


class UpdateProfile(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = 'registration/update_profile.html'
    success_url = reverse_lazy("my_profile")
    success_message = "Profile updated"

    def get_object(self, queryset=None):
        user = self.request.user
        return user


class UserProfile(LoginRequiredMixin, DetailView):
    model = User
    template_name = "registration/profile.html"

    def get_object(self, queryset=None):
        user = self.request.user
        return user


class AuthorsListView(ListView):
    model = User
    paginate_by = 10
    template_name = 'accounts/authors_list.html'


def view_user_profile(request, pk):
    user = User.objects.get(pk=pk)
    page = request.GET.get('page', 1)
    posts = Post.objects.filter(author=user)
    paginator = Paginator(posts, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'accounts/authors.html', {
        'profile': user,
        'posts': posts
    })


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):

        comments = Comment.objects.filter(published=True, posts=self.get_object())
        paginator = Paginator(comments, 5)
        page_num = int(self.request.GET.get('page', 1))
        page = paginator.page(page_num)
        context = super().get_context_data(**kwargs)
        context['comments'] = comments
        context['paginator'] = paginator
        context['page_obj'] = page
        context['is_paginated'] = True
        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)

        return context


class PostListView(ListView):
    model = Post
    paginate_by = 10
    ordering = ['title']
    queryset = Post.objects.select_related('author').prefetch_related('comment_set')


class PostUpdateDetailView(LoginRequiredMixin, DetailView):
    model = Post
    paginate_by = 10
    template_name = 'accounts/post_update_detail.html'

    def get_context_data(self, **kwargs):
        comments = Comment.objects.filter(posts=self.get_object())
        paginator = Paginator(comments, 5)
        page_num = int(self.request.GET.get('page', 1))
        page = paginator.page(page_num)
        context = super().get_context_data(**kwargs)
        context['comments'] = comments
        context['paginator'] = paginator
        context['page_obj'] = page
        context['is_paginated'] = True
        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)
        return context


class PostUpdateListView(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 10
    ordering = ['title']
    template_name = 'accounts/post_update_list.html'
    queryset = Post.objects.select_related('author')

    def get_context_data(self, **kwargs):
        object_list = Post.objects.filter(author=self.request.user)
        context = super(PostUpdateListView, self).get_context_data(object_list=object_list, **kwargs)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'short_description', 'full_description', 'image', 'data_post']

    def form_valid(self, form):
        subjects = form.cleaned_data.get('author')
        message = form.cleaned_data.get('title')
        celery_send_mail.delay(subject=subjects, message=message, from_email='my-blog@gmail.com')
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(DeleteView):
    model = Post
    queryset = Post.objects.select_related('author')

    def get_context_data(self, **kwargs):
        object_list = Post.objects.filter(author=self.request.user)
        context = super(PostDeleteView, self).get_context_data(object_list=object_list, **kwargs)
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'title', 'short_description', 'full_description', 'image', 'data_post']
    template_name = "accounts/post_update.html"
    queryset = Post.objects.select_related('author')

    def get_context_data(self, **kwargs):
        object_list = Post.objects.filter(author=self.request.user)
        context = super(PostUpdateView, self).get_context_data(object_list=object_list, **kwargs)
        return context

    def form_valid(self, form):
        form.instance.posts = Post.objects.get(pk=self.kwargs['pk'])
        return super(PostUpdateView, self).form_valid(form)


class CommentListView(ListView):
    model = Comment
    paginate_by = 10
    ordering = ['text_comment']
    queryset = Comment.objects.select_related('posts')


class CommentDetailView(DetailView):
    model = Comment


class CommentCreateView(CreateView):
    model = Comment
    fields = ['username', 'text_comment']

    def form_valid(self, form):
        post = str(Post.objects.get(pk=self.kwargs['pk']))
        subjects = form.cleaned_data.get('username')
        comment = form.cleaned_data.get('text_comment')

        send_mail_comment.delay(subject=post, message=comment, from_email='my-blog@gmail.com')

        send_mail_to_user.delay(subject=subjects, message=post)

        form.instance.posts = Post.objects.get(pk=self.kwargs['pk'])
        return super(CommentCreateView, self).form_valid(form)