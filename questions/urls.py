from django.urls import path

from questions import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('ask', views.ask, name='ask'),
    path('profile', views.profile, name='profile'),
    path('question', views.question, name='question'),
    path('signup', views.signup, name='signup'),
]