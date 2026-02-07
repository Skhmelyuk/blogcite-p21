from django import forms
from django.core.validators import EmailValidator

class ContactForm(forms.Form):
  name = forms.CharField(
    max_length=100,
    label='Ім\'я',
    widget=forms.TextInput(attrs={
      'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
      'placeholder': 'Введіть ваше ім\'я',
      'required': True,
    }),
    error_messages={
      'required': 'Будь ласка, введіть ваше ім\'я.',
      'max_length': 'Ім\'я не може бути довшим за 100 символів.',
    }
  )

  email = forms.EmailField(
    label='Email',
    validators=[EmailValidator(message='Введіть коректну email адресу.')],
    widget=forms.EmailInput(attrs={
      'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
      'placeholder': 'your.email@example.com',
      'required': True,
    }),
    error_messages={
      'required': 'Будь ласка, введіть вашу email адресу.',
      'invalid': 'Введіть коректну email адресу.',
    }
  )

  subject = forms.CharField(
    max_length=200,
    label='Тема',
    widget=forms.TextInput(attrs={
      'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
      'placeholder': 'Тема повідомлення',
      'required': True,
    }),
    error_messages={
      'required': 'Будь ласка, введіть тему повідомлення.',
      'max_length': 'Тема не може бути довшою за 200 символів.',
    }
  )
    
  message = forms.CharField(
    label='Повідомлення',
    widget=forms.Textarea(attrs={
      'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none',
      'placeholder': 'Ваше повідомлення...',
      'rows': 6,
      'required': True,
    }),
    error_messages={
      'required': 'Будь ласка, введіть ваше повідомлення.',
    }
  )
    
  def clean_name(self):
    """Валідація поля імені"""
    name = self.cleaned_data.get('name')
    if len(name) < 2:
      raise forms.ValidationError(
        'Ім\'я повинно містити щонайменше 2 символи.'
      )
    # Перевірка на спам (тільки цифри)
    if name.isdigit():
      raise forms.ValidationError(
        'Ім\'я не може складатися лише з цифр.'
      )
    return name.strip()
    
  def clean_message(self):
    """Валідація поля повідомлення"""
    message = self.cleaned_data.get('message')
    if len(message) < 10:
      raise forms.ValidationError(
        'Повідомлення повинно містити щонайменше 10 символів.'
      )
    # Перевірка на спам (багато посилань)
    if message.lower().count('http') > 3:
      raise forms.ValidationError(
        'Повідомлення містить занадто багато посилань.'
      )
    return message.strip()
    
  def clean_subject(self):
    """Валідація поля теми"""
    subject = self.cleaned_data.get('subject')
    return subject.strip()