import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker

from questions.models import (
    Question,
    Answer,
    Tag,
    Profile,
    QuestionReaction,
)

fake = Faker()


class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options['ratio']

        self.stdout.write(
            self.style.SUCCESS(f'Start filling DB with ratio={ratio}')
        )

        self.clear_db()

        users = self.create_users(ratio)
        tags = self.create_tags(ratio)
        questions = self.create_questions(ratio, users, tags)

        self.create_answers(ratio, users, questions)
        self.create_reactions(ratio, users, questions)

        self.stdout.write(self.style.SUCCESS('DONE'))

    def clear_db(self):
        QuestionReaction.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Profile.objects.all().delete()
        Tag.objects.all().delete()

        # если нужен superuser — можно удалить эту строку
        User.objects.filter(is_superuser=False).delete()

    def create_users(self, ratio):
        fake.unique.clear()

        users = []

        for i in range(ratio):
            users.append(
                User(
                    username=f'user_{i}_{fake.user_name()}',
                    email=fake.unique.email(),
                )
            )

        User.objects.bulk_create(users, batch_size=1000)

        users = list(User.objects.all())

        profiles = [
            Profile(
                user=user,
                email=user.email,
                nickname=fake.user_name(),
            )
            for user in users
        ]

        Profile.objects.bulk_create(profiles, batch_size=1000)

        self.stdout.write(self.style.SUCCESS('Users created'))

        return users

    def create_tags(self, ratio):
        fake.unique.clear()

        tag_count = max(20, ratio // 100)

        tags = [
            Tag(name=fake.unique.word())
            for _ in range(tag_count)
        ]

        Tag.objects.bulk_create(tags, batch_size=1000)

        tags = list(Tag.objects.all())

        self.stdout.write(self.style.SUCCESS('Tags created'))

        return tags

    def create_questions(self, ratio, users, tags):
        questions = [
            Question(
                title=fake.sentence()[:50],
                body=fake.text(max_nb_chars=500),
                user=random.choice(users),
                rating=random.randint(0, 100),
            )
            for _ in range(ratio)
        ]

        Question.objects.bulk_create(questions, batch_size=1000)

        questions = list(Question.objects.all())

        # BULK CREATE ДЛЯ MANY-TO-MANY
        through_model = Question.tags.through
        relations = []

        for question in questions:
            selected_tags = random.sample(
                tags,
                k=min(3, len(tags))
            )

            for tag in selected_tags:
                relations.append(
                    through_model(
                        question_id=question.id,
                        tag_id=tag.id,
                    )
                )

        through_model.objects.bulk_create(
            relations,
            batch_size=1000
        )

        self.stdout.write(self.style.SUCCESS('Questions created'))

        return questions

    def create_answers(self, ratio, users, questions):
        answers = [
            Answer(
                question=random.choice(questions),
                user=random.choice(users),
                body=fake.text(max_nb_chars=300),
                rating=random.randint(0, 50),
            )
            for _ in range(ratio)
        ]

        Answer.objects.bulk_create(answers, batch_size=1000)

        self.stdout.write(self.style.SUCCESS('Answers created'))

    def create_reactions(self, ratio, users, questions):
        reactions = []
        used_pairs = set()

        target = ratio

        while len(reactions) < target:
            user = random.choice(users)
            question = random.choice(questions)

            pair = (user.id, question.id)

            if pair in used_pairs:
                continue

            used_pairs.add(pair)

            reactions.append(
                QuestionReaction(
                    question=question,
                    user=user,
                    positive=random.choice([True, False]),
                )
            )

        QuestionReaction.objects.bulk_create(
            reactions,
            batch_size=1000
        )

        self.stdout.write(self.style.SUCCESS('Reactions created'))