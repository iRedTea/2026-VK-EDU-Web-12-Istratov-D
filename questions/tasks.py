from __future__ import annotations
from celery import shared_task
from django.core.cache import cache
from django.conf import settings
import requests
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Q
from django.contrib.auth.models import User
from .models import Tag, Question, Answer



@shared_task
def rebuild_popular_tags():
    # compute top 10 tags by number of questions in last 3 months
    three_months_ago = timezone.now() - timedelta(days=90)
    popular_qs = Tag.objects.annotate(
        q_count=Count('question', filter=Q(question__created_at__gte=three_months_ago))
    ).order_by('-q_count')[:10]

    popular = [
        {'name': t.name, 'count': t.q_count}
        for t in popular_qs
    ]
    # store in cache
    cache.set('popular_tags', popular, timeout=60 * 60)
    return popular


@shared_task
def rebuild_best_members():
    # compute top 10 users by activity (questions created in last week + total answers)
    week_ago = timezone.now() - timedelta(days=7)

    # users with most questions in the last week (by count)
    users_q = User.objects.annotate(
        q_count=Count('question', filter=Q(question__created_at__gte=week_ago))
    )

    # users with most answers in the last week
    users_a = User.objects.annotate(
        a_count=Count('answer', filter=Q(answer__created_at__gte=week_ago))
    )

    # combine scores
    scores = {}

    for u in users_q:
        scores[u.id] = scores.get(u.id, 0) + (u.q_count or 0)

    for u in users_a:
        scores[u.id] = scores.get(u.id, 0) + (u.a_count or 0)

    # build list of users sorted by score
    best_users = User.objects.filter(id__in=list(scores.keys()))
    best = []
    for u in best_users:
        best.append({
            'id': u.id,
            'username': u.username,
            'score': scores.get(u.id, 0)
        })

    best.sort(key=lambda x: x['score'], reverse=True)
    best = best[:10]

    cache.set('best_members', best, timeout=60 * 60)
    return best


@shared_task
def publish_new_answer_centrifugo(question_id: int, payload: dict):
    # Send message to centrifugo pushed via HTTP API
    # Use Centrifugo HTTP API (v4) publish endpoint
    api_url = settings.CENTRIFUGO_URL.rstrip('/') + '/api'
    headers = {'Authorization': f'apikey {settings.CENTRIFUGO_API_KEY}'}
    data = {
        'method': 'publish',
        'params': {
            'channel': f'question_{question_id}',
            'data': payload,
        }
    }
    try:
        requests.post(api_url, json=data, headers=headers, timeout=5)
    except Exception:
        pass


@shared_task
def send_new_answer_email(subject: str, message: str, recipient_list: list[str]):
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
