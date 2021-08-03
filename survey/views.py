from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.csrf import csrf_protect
from django.views.generic.list import ListView
from survey.models import Question, Answer


class QuestionListView(ListView):
    model = Question

    def get_ordered_questions(self):
        questions = list(Question.objects.order_by('-created')[:20])
        rankings = [question.ranking for question in questions]
        rankings.sort(reverse=True)
        ordered_questions = []
        for ranking in rankings:
            total_questions = rankings.count(ranking)
            for question in questions:
                if question.ranking == ranking:
                    ordered_questions.append(
                        questions.pop(questions.index(question))
                    )
                    if total_questions <= 1:
                        break
                    total_questions -= 1

        return ordered_questions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = self.get_ordered_questions()
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return context
        object_list = []
        for question in context.get('object_list'):
            question.user_value = self.user_value(user, question)
            question.user_likes = self.user_likes(user, question)
            question.user_dislikes = self.user_dislikes(user, question)
            object_list.append(question)
        if object_list:
            context['object_list'] = object_list
        return context

    def user_value(self, user, question):
        answer = Answer.objects.filter(question=question, author=user).first()
        if answer:
            return answer.value
        else:
            return 0

    def user_likes(self, user, question):
        answer = Answer.objects.filter(question=question, author=user).first()
        if answer:
            return answer.like_dislike == True
        else:
            return None

    def user_dislikes(self, user, question):
        answer = Answer.objects.filter(question=question, author=user).first()
        if answer:
            return answer.like_dislike == False
        else:
            return None


class QuestionCreateView(CreateView):
    model = Question
    fields = ['title', 'description']
    redirect_url = ''

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)


class QuestionUpdateView(UpdateView):
    model = Question
    fields = ['title', 'description']
    template_name = 'survey/question_form.html'


@login_required
def answer_question(request):
    question_pk = request.POST.get('question_pk')
    if not request.POST.get('question_pk'):
        return JsonResponse({'ok': False})
    question = Question.objects.filter(pk=question_pk)[0]
    answer, _ = Answer.objects.get_or_create(
        question=question, author=request.user
    )
    if answer.value != request.POST.get('value'):
        answer.value = request.POST.get('value')
        answer.save()
    return JsonResponse({'ok': True})


@login_required
def like_dislike_question(request):
    question_pk = request.POST.get('question_pk')
    if not request.POST.get('question_pk'):
        return JsonResponse({'ok': False})
    question = Question.objects.filter(pk=question_pk)[0]
    answer, created = Answer.objects.get_or_create(
        question=question, author=request.user
    )
    like_dislike = int(request.POST.get('like_dislike'))
    if not created and answer.like_dislike == like_dislike:
        return JsonResponse({'ok': True})
    old_like_dislike = answer.like_dislike
    answer.like_dislike = bool(like_dislike)
    answer.save()
    if like_dislike == 1:
        question.like += 1
    else:
        question.dislike += 1
    if not created:
        if old_like_dislike:
            question.like -= 1
        else:
            question.dislike -= 1
    question.save()
    return JsonResponse({'ok': True})

