from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import Count, Q

from .models import Tag


def sidebar_data(request):
    popular_tags = cache.get('popular_tags')
    best_members = cache.get('best_members')

    if popular_tags is None:
        three_months_ago = timezone.now() - timedelta(days=90)
        popular_qs = Tag.objects.annotate(
            q_count=Count('question', filter=Q(question__created_at__gte=three_months_ago))
        ).order_by('-q_count')[:10]
        popular_tags = [
            {'name': tag.name, 'count': tag.q_count}
            for tag in popular_qs
        ]
        cache.set('popular_tags', popular_tags, timeout=60 * 60)

    if best_members is None:
        week_ago = timezone.now() - timedelta(days=7)
        users_q = User.objects.annotate(
            q_count=Count('question', filter=Q(question__created_at__gte=week_ago))
        )
        users_a = User.objects.annotate(
            a_count=Count('answer', filter=Q(answer__created_at__gte=week_ago)))

        scores = {}
        for u in users_q:
            scores[u.id] = scores.get(u.id, 0) + (u.q_count or 0)
        for u in users_a:
            scores[u.id] = scores.get(u.id, 0) + (u.a_count or 0)

        best_members_list = User.objects.filter(id__in=list(scores.keys()))
        best_members = [
            {
                'id': u.id,
                'username': u.username,
                'score': scores.get(u.id, 0)
            }
            for u in best_members_list
        ]
        best_members.sort(key=lambda x: x['score'], reverse=True)
        best_members = best_members[:10]
        cache.set('best_members', best_members, timeout=60 * 60)

    return {
        'popular_tags': popular_tags,
        'best_members': best_members,
    }
