from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import ContactForm


def contact_view(request):
  """Function-based view для контактної форми"""
  if request.method == 'POST':
    form = ContactForm(request.POST)
    if form.is_valid():
      # Отримуємо дані з форми
      name = form.cleaned_data['name']
      email = form.cleaned_data['email']
      subject = form.cleaned_data['subject']
      message = form.cleaned_data['message']
            
      # Формуємо email повідомлення
      email_subject = f"Контактна форма: {subject}"
      email_message = f"""
Нове повідомлення з контактної форми

Від: {name}
Email: {email}
Тема: {subject}

Повідомлення:
{message}

---
Це повідомлення надіслано з контактної форми сайту.
"""
            
      # Відправляємо email
      try:
        send_mail(
            subject=email_subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        messages.success(
            request,
            'Дякуємо за ваше повідомлення! Ми зв\'яжемося з вами найближчим часом.'
        )
        return redirect('contact:success')
            
      except BadHeaderError:
        messages.error(
            request,
            'Виявлено некоректний заголовок email.'
        )
      except Exception as e:
        messages.error(
            request,
            f'Виникла помилка при відправці повідомлення. Спробуйте пізніше.'
        )
        # Для розробки можна вивести помилку
        if settings.DEBUG:
            print(f"Email error: {e}")
    else:
        messages.error(
            request,
            'Будь ласка, виправте помилки у формі.'
        )
  else:
    form = ContactForm()
    
  return render(request, 'contact/contact_form.html', {'form': form})


def contact_success_view(request):
    """Сторінка успішної відправки"""
    return render(request, 'contact/success.html')
