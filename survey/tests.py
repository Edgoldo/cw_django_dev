from random import randint

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from survey.models import Question, Answer


class SurveyTest(TestCase):
    questions_data = [
        {
            'title': 'Is this the first question?',
            'description': 'Yes, it is.'
        },
        {
            'title': 'How do you run this test?',
            'description': 'Runs python manage.py test in your terminal.'
        },
        {
            'title': 'The data of this test will be deleted?',
            'description': 'Yes, that is right.'
        }
    ]
    answers_data = [
        {
            'username': 'user1',
            'password': 'thepass123',
            'value': randint(0, 5),
            'like_dislike': randint(0, 1)
        },
        {
            'username': 'user2',
            'password': 'thepass123',
            'value': randint(0, 5),
            'like_dislike': randint(0, 1)
        },
        {
            'username': 'user3',
            'password': 'thepass123',
            'value': randint(0, 5)
        }
    ]

    def setUp(self):
        users_data = [
            {
                'username': 'user1',
                'email': 'user1@test.com'
            },
            {
                'username': 'user2',
                'email': 'user2@test.com'
            },
            {
                'username': 'user3',
                'email': 'user3@test.com'
            }
        ]
        # Create Users
        for user_data in users_data:
            user = User(**user_data)
            user.set_password("thepass123")
            user.save()

        # Create Questions
        for question_data in self.questions_data:
            question_data['author_id'] = User.objects.first().id
            question = Question.objects.update_or_create(**question_data)
        questions = Question.objects.all()
        # Create Answers
        for answer_data in self.answers_data:
            answer_data = answer_data.copy()
            self.client.login(
                username=answer_data.pop("username"),
                password=answer_data.pop("password")
            )
            question_id = questions[randint(1, questions.count() - 1)].id
            answer_data['question_id'] = question_id
            answer_data['author_id'] = self.client.session.get('_auth_user_id')
            answer = Answer.objects.update_or_create(**answer_data)

    def create_questions(self, data):
        """Make POST request to create a question"""

        url = reverse("survey:question-create")
        response = self.client.post(url, data)
        questions = Question.objects.filter(**data)
        self.assertEqual(questions.count(), 2)

    def test_question(self):
        """Test the question registers"""

        questions = Question.objects.all()
        self.assertEqual(questions.count(), 3)
        self.client.login(username="user1", password="thepass123")
        for data in self.questions_data:
            self.create_questions(data)
        questions = Question.objects.all()
        self.assertEqual(questions.count(), 6)

    def create_answer(self, data):
        """Function that make POST request to create Answers"""

        self.client.login(
            username=data.get("username"), password=data.get("password")
        )
        data = {
            'question_pk': data.get("question_id"),
            'value': data.get("value")
        }
        url = reverse("survey:question-answer")
        response = self.client.post(url, data)
        answers = Answer.objects.filter(
            author=self.client.session.get('_auth_user_id')
        )
        self.assertEqual(response.status_code, 200)
        url = reverse("survey:question-answer")
        like_dislike = data.get('like_dislike', -1)
        if like_dislike >= 0:
            data['like_dislike'] = like_dislike
        response = self.client.post(url, data)
        response_json = response.json()
        if like_dislike >= 0:
            self.assertEqual(response_json.get('ok'), False)
        self.assertEqual(response_json.get('ok'), True)

    def test_questions_answers(self):
        """Test POST request to create Answers"""
        questions = Question.objects.all()
        for data in self.answers_data:
            question_id = questions[randint(1, questions.count() - 1)].id
            data['question_id'] = question_id
            self.create_answer(data)

    def test_ranking_order(self):
        questions = Question.objects.all()
        rankings = [q.ranking for q in questions]
        rankings.sort(reverse=True)
        url = reverse("survey:question-list")
        response = self.client.get(url)
        questions_response = response.context[0].get('object_list')
        rankings_response = [q.ranking for q in questions_response]
        self.assertEqual(rankings_response, rankings)
