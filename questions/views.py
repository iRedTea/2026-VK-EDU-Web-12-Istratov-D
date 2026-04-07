from django.shortcuts import render
from django.core.paginator import Paginator


QUESTIONS = [
    {
        "id": i,
        "title": f'Question number {i}',
        "text": f'Some text {i}',
    }
    for i in range(10)
]

def index(request):
    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1
    page = Paginator(QUESTIONS, 4)
    page_obj = page.page(page_number)
    return render(request, 'core/index.html', context={'questions': page_obj.object_list, 'page_obj': page_obj})


def ask(request):
    return render(request, 'core/ask.html', context={'questions': QUESTIONS})


def login(request):
    return render(request, 'core/login.html', context={'questions': QUESTIONS})

def profile(request):
    return render(request, 'core/profile.html', context={'questions': QUESTIONS})

def question(request):
    return render(request, 'core/question.html', context={'questions': QUESTIONS})

def signup(request):
    return render(request, 'core/signup.html', context={'questions': QUESTIONS})