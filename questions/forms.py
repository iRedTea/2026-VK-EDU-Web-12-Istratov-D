from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

import os

from .models import Question, Tag
from .models import Profile
from .models import Answer

def validate_avatar(image):
    max_size = 2 * 1024 * 1024

    if image.size > max_size:
        raise ValidationError("Image too large (max 2MB)")

    ext = os.path.splitext(image.name)[1].lower()

    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.ico']

    if ext not in allowed_extensions:
        raise ValidationError("Unsupported file extension")

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise ValidationError("Wrong login or password")

        cleaned_data['user'] = user
        return cleaned_data


class SignupForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    nickname = forms.CharField(max_length=100)

    password = forms.CharField(widget=forms.PasswordInput)
    password_repeat = forms.CharField(widget=forms.PasswordInput)

    avatar = forms.ImageField(
        required=False,
        validators=[validate_avatar]
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if Profile.objects.filter(email=email).exists():
            raise ValidationError("Email already registered")
        return email

    def clean(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_repeat')

        if p1 != p2:
            raise ValidationError("Passwords do not match")

        validate_password(p1)

        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )

        Profile.objects.create(
            user=user,
            email=self.cleaned_data['email'],
            nickname=self.cleaned_data['nickname'],
            avatar=self.cleaned_data.get('avatar')
        )

        return user


class ProfileForm(forms.Form):
    email = forms.EmailField()
    nickname = forms.CharField(max_length=100)
    avatar = forms.ImageField(
        required=False,
        validators=[validate_avatar]
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user:
            self.fields['email'].initial = user.profile.email
            self.fields['nickname'].initial = user.profile.nickname

    def clean_email(self):
        email = self.cleaned_data['email']

        if Profile.objects.filter(email=email).exclude(user=self.user).exists():
            raise ValidationError("Email already used")

        return email

    def save(self):
        profile = self.user.profile

        profile.email = self.cleaned_data['email']
        profile.nickname = self.cleaned_data['nickname']

        if self.cleaned_data.get('avatar'):
            profile.avatar = self.cleaned_data['avatar']

        profile.save()

class AskForm(forms.ModelForm):
    tags = forms.CharField()

    class Meta:
        model = Question
        fields = ['title', 'body']

    def clean_tags(self):
        tags = self.cleaned_data['tags'].split(',')
        tags = [t.strip() for t in tags if t.strip()]

        if not tags:
            raise ValidationError("Add at least one tag")

        return tags

    def save(self, user):
        question = super().save(commit=False)
        question.user = user
        question.save()

        tags = self.cleaned_data['tags']

        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            question.tags.add(tag)

        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['body']

    def save(self, user, question):
        answer = super().save(commit=False)
        answer.user = user
        answer.question = question
        answer.save()
        return answer