from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from .models import (
    Question,
    Tag,
    Answer,
    QuestionReaction,
    AnswerReaction
)

from .forms import (
    LoginForm,
    SignupForm,
    ProfileForm,
    AskForm,
    AnswerForm
)
from . import tasks as tasks_module


def index(request):

    tag_name = request.GET.get('tag')

    questions = Question.objects.all() \
        .select_related('user') \
        .prefetch_related('tags') \
        .order_by('-created_at')

    if tag_name:
        questions = questions.filter(tags__name=tag_name)

    paginator = Paginator(questions, 4)

    page_number = request.GET.get('page', 1)

    page_obj = paginator.get_page(page_number)

    user_reactions = {}

    if request.user.is_authenticated:

        reactions = QuestionReaction.objects.filter(
            user=request.user,
            question__in=page_obj.object_list
        )

        user_reactions = {
            reaction.question_id: reaction.positive
            for reaction in reactions
        }

    hot_questions = Question.objects.order_by('-rating')[:4]

    return render(request, 'core/index.html', {
        'questions': page_obj.object_list,
        'page_obj': page_obj,
        'hot_questions': hot_questions,
        'tags': Tag.objects.all(),
        'tag': tag_name,
        'user_reactions': user_reactions
    })


def hot(request):

    questions = Question.objects.all() \
        .select_related('user') \
        .prefetch_related('tags') \
        .order_by('-rating')

    paginator = Paginator(questions, 4)

    page_number = request.GET.get('page', 1)

    page_obj = paginator.get_page(page_number)

    user_reactions = {}

    if request.user.is_authenticated:

        reactions = QuestionReaction.objects.filter(
            user=request.user,
            question__in=page_obj.object_list
        )

        user_reactions = {
            reaction.question_id: reaction.positive
            for reaction in reactions
        }

    return render(request, 'core/hot.html', {
        'questions': page_obj.object_list,
        'page_obj': page_obj,
        'hot_questions': questions[:4],
        'tags': Tag.objects.all(),
        'user_reactions': user_reactions
    })


def search(request):
    query_text = request.GET.get('q', '').strip()

    if not query_text:
        return JsonResponse({'results': []})

    vector = SearchVector('title', 'body')
    query = SearchQuery(query_text)
    questions = Question.objects.annotate(
        rank=SearchRank(vector, query)
    ).filter(rank__gte=0.1).order_by('-rank')[:10]

    results = [
        {
            'id': q.id,
            'title': q.title,
            'url': f'/question?question_id={q.id}'
        }
        for q in questions
    ]

    return JsonResponse({'results': results})


def question(request):

    question_id = request.GET.get('question_id')

    question = get_object_or_404(
        Question.objects.select_related('user')
        .prefetch_related('tags', 'answers'),
        id=question_id
    )

    if request.method == 'POST':

        if not request.user.is_authenticated:
            return redirect(
                f'/login?next=/question?question_id={question_id}'
            )

        form = AnswerForm(request.POST)

        if form.is_valid():

            answer = form.save(
                user=request.user,
                question=question
            )

            # trigger async notifications and cache updates
            try:
                payload = {
                    'id': answer.id,
                    'body': answer.body,
                    'user': answer.user.username
                }
                tasks_module.publish_new_answer_centrifugo.delay(question.id, payload)
            except Exception:
                pass

            try:
                # send email to question author
                recipient = []
                if hasattr(question.user, 'profile'):
                    recipient = [question.user.profile.email]
                subject = f'New answer to your question: {question.title}'
                message = f'User {answer.user.username} answered your question.\n\n{answer.body}'
                if recipient and recipient[0]:
                    tasks_module.send_new_answer_email.delay(subject, message, recipient)
            except Exception:
                pass

            # optionally trigger cache rebuilds
            try:
                tasks_module.rebuild_popular_tags.delay()
                tasks_module.rebuild_best_members.delay()
            except Exception:
                pass

            return redirect(
                f'/question?question_id={question.id}#answer-{answer.id}'
            )

    else:

        form = AnswerForm()

    question_reaction = None

    answer_reactions = {}

    if request.user.is_authenticated:

        question_reaction = QuestionReaction.objects.filter(
            question=question,
            user=request.user
        ).first()

        reactions = AnswerReaction.objects.filter(
            user=request.user,
            answer__question=question
        )

        answer_reactions = {
            reaction.answer_id: reaction.positive
            for reaction in reactions
        }

    return render(request, 'core/question.html', {
        'question': question,
        'answers': question.answers.all(),
        'form': form,
        'tags': Tag.objects.all(),
        'question_reaction': question_reaction,
        'answer_reactions': answer_reactions
    })


def login(request):

    next_url = request.GET.get('next', '/')

    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            user = form.cleaned_data['user']

            auth_login(request, user)

            if not url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()}
            ):
                next_url = '/'

            return redirect(next_url)

    else:

        form = LoginForm()

    return render(request, 'core/login.html', {
        'form': form,
        'next': next_url,
        'tags': Tag.objects.all()
    })


def signup(request):

    if request.method == 'POST':

        form = SignupForm(request.POST, request.FILES)

        if form.is_valid():

            user = form.save()

            auth_login(request, user)

            return redirect('/')

    else:

        form = SignupForm()

    return render(request, 'core/signup.html', {
        'form': form,
        'tags': Tag.objects.all()
    })


def logout(request):

    auth_logout(request)

    return redirect(
        request.META.get('HTTP_REFERER', '/')
    )


@login_required
def profile(request):

    if request.method == 'POST':

        form = ProfileForm(
            request.POST,
            request.FILES,
            user=request.user
        )

        if form.is_valid():

            form.save()

            return redirect('profile')

    else:

        form = ProfileForm(user=request.user)

    return render(request, 'core/profile.html', {
        'form': form,
        'tags': Tag.objects.all()
    })


@login_required
def ask(request):

    if request.method == 'POST':

        form = AskForm(request.POST)

        if form.is_valid():

            question = form.save(user=request.user)

            return redirect(
                f'/question?question_id={question.id}'
            )

    else:

        form = AskForm()

    return render(request, 'core/ask.html', {
        'form': form,
        'tags': Tag.objects.all()
    })


@require_POST
@login_required
def question_react(request):

    question_id = request.POST.get('question_id')

    reaction_type = request.POST.get('type')

    if reaction_type not in ['like', 'dislike']:

        return JsonResponse({
            'error': 'invalid type'
        }, status=400)

    question = get_object_or_404(
        Question,
        id=question_id
    )

    if QuestionReaction.objects.filter(
        question=question,
        user=request.user
    ).exists():

        return JsonResponse({
            'error': 'already reacted'
        }, status=400)

    positive = reaction_type == 'like'

    QuestionReaction.objects.create(
        question=question,
        user=request.user,
        positive=positive
    )

    if positive:
        question.rating += 1
    else:
        question.rating -= 1

    question.save()

    return JsonResponse({
        'rating': question.rating
    })


@require_POST
@login_required
def answer_react(request):

    answer_id = request.POST.get('answer_id')

    reaction_type = request.POST.get('type')

    if reaction_type not in ['like', 'dislike']:

        return JsonResponse({
            'error': 'invalid type'
        }, status=400)

    answer = get_object_or_404(
        Answer,
        id=answer_id
    )

    if AnswerReaction.objects.filter(
        answer=answer,
        user=request.user
    ).exists():

        return JsonResponse({
            'error': 'already reacted'
        }, status=400)

    positive = reaction_type == 'like'

    AnswerReaction.objects.create(
        answer=answer,
        user=request.user,
        positive=positive
    )

    if positive:
        answer.rating += 1
    else:
        answer.rating -= 1

    answer.save()

    return JsonResponse({
        'rating': answer.rating
    })


@require_POST
@login_required
def mark_correct(request):

    question_id = request.POST.get('question_id')

    answer_id = request.POST.get('answer_id')

    question = get_object_or_404(
        Question,
        id=question_id
    )

    answer = get_object_or_404(
        Answer,
        id=answer_id
    )

    if question.user != request.user:

        return JsonResponse({
            'error': 'forbidden'
        }, status=403)

    if answer.question != question:

        return JsonResponse({
            'error': 'wrong answer'
        }, status=400)

    question.correct_answer = answer

    question.save()

    return JsonResponse({
        'success': True,
        'correct_answer_id': answer.id
    })