from .models import Post, Comment
from celery import shared_task
from django.core.mail import send_mail as django_send_mail


@shared_task
def send_mail(subject, message, from_email):
    post = Post.objects.get(title=message)
    message_email = "Created a new post:\npost_id: {post_id}\npost_title: {post_title}\n" \
                    "post_author: {author}\n" \
                    "create_data: {data}" \
                    " \nWaiting for publication".format(post_id=post.pk, post_title=post.title, author=post.author,
                                                        data=post.data_post)
    django_send_mail(subject, message_email, from_email, ['admin@example.com'])


@shared_task
def send_mail_to_user(subject, message):
    post = Post.objects.get(title=message)
    title = post.title
    pk = post.pk
    email = post.author.email
    link_post = "You have a new comment on the post: {title}\n" \
                "Link post: http://127.0.0.1:8000/accounts/posts/{pk}".format(pk=pk, title=title)
    django_send_mail(subject, link_post, "user_blog@gmail.com", [email])


@shared_task
def send_mail_comment(subject, message, from_email):
    post = Post.objects.get(title=subject)
    comment = Comment.objects.get(text_comment=message)

    message_email = "Created a new comment:\n comment id:{comment}\ncomment text: {text}\n" \
                    "author: {author}\n" \
                    "post: {post}" \
                    " \nWaiting for publication".format(comment=comment.id,
                                                        text=comment.text_comment, author=comment.username,
                                                        post=post)
    django_send_mail(subject, message_email, from_email, ['admin@example.com'])


@shared_task
def send_mail_contact(subject, message, from_email):
    django_send_mail(subject, message, from_email, ['admin@example.com'])
