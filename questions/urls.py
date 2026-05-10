from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from questions import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('ask', views.ask, name='ask'),
    path('profile', views.profile, name='profile'),
    path('question', views.question, name='question'),
    path('signup', views.signup, name='signup'),
    path('hot', views.hot, name='hot'),
    path('logout', views.logout, name='logout'),
    path('ajax/question/react/', views.question_react),
    path('ajax/answer/react/', views.answer_react),
    path('ajax/answer/correct/', views.mark_correct),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)