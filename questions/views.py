from django.shortcuts import render
from django.core.paginator import Paginator


QUESTIONS = [
    {
        "id": i,
        "title": f'Question number {i}',
        "text": f'Some text {i}',
        "tags": ["python"],
    }
    for i in range(10)
]

HOT_QUESTIONS = QUESTIONS[:4]

TAGS = {tag for q in QUESTIONS for tag in q["tags"]}

def index(request):
    tag = request.GET.get('tag', '')
    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1
    page = Paginator(QUESTIONS if tag == ''
                     else [ cur_question for cur_question in QUESTIONS if tag in cur_question['tags']], 4)
    page_obj = page.page(page_number)

    return render(request, 'core/index.html', context={'questions': page_obj.object_list,
                                                       'hot_questions': HOT_QUESTIONS, 'page_obj': page_obj, 'tags': TAGS,
                                                       'tag': tag})

def ask(request):
    return render(request, 'core/ask.html', context={'questions': QUESTIONS, 'tags': TAGS})
def hot(request):
    return render(request, 'core/hot.html', context={'questions': QUESTIONS, 'tags': TAGS,
                                                     'hot_questions': HOT_QUESTIONS,})

def login(request):
    return render(request, 'core/login.html', context={'questions': QUESTIONS, 'tags': TAGS})

def profile(request):
    return render(request, 'core/profile.html', context={'questions': QUESTIONS, 'tags': TAGS})

def question(request):
    return render(request, 'core/question.html', context={'questions': QUESTIONS, 'tags': TAGS})

def signup(request):
    return render(request, 'core/signup.html', context={'questions': QUESTIONS, 'tags': TAGS})