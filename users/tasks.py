from celery import shared_task
import time
import datetime
from django.core.mail import send_mail


@shared_task
def long_running_task(n):
    time.sleep(n)
    return f"Задача завершилась за {n} секунд"

@shared_task
def print_hello():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] Привет из Celery!")

@shared_task
def send_welcome_email(to_email):
    send_mail(
        subject="Добро пожаловать!",
        message="Спасибо за регистрацию!",
        from_email="your_email@gmail.com",
        recipient_list=[to_email],
        fail_silently=False,
    )
    return f"Письмо отправлено на {to_email}"