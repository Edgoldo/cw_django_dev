from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


class Question(models.Model):
    created = models.DateField('Creada', auto_now_add=True)
    author = models.ForeignKey(get_user_model(), related_name="questions", verbose_name='Pregunta',
                               on_delete=models.CASCADE)
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descripción')
    like = models.PositiveIntegerField(default=0)
    dislike = models.PositiveIntegerField(default=0)

    @property
    def ranking(self):
        QUESTION_POINTS = {
            'answers': 10,
            'likes': 5,
            'dislikes': 3,
            'today': 10
        }
        answers = Answer.objects.filter(
            question=self, value__gt=0
        ).count()
        today = datetime.now()
        today_points = 0
        if self.created == today:
            today_points = QUESTION_POINTS['today']
        ranking = (
            answers*QUESTION_POINTS['answers'] +
            self.like*QUESTION_POINTS['likes'] -
            self.dislike*QUESTION_POINTS['dislikes'] +
            today_points
        )
        return ranking

    def get_absolute_url(self):
        return reverse('survey:question-edit', args=[self.pk])


class Answer(models.Model):
    ANSWERS_VALUES = ((0,'Sin Responder'),
                      (1,'Muy Bajo'),
                      (2,'Bajo'),
                      (3,'Regular'),
                      (4,'Alto'),
                      (5,'Muy Alto'),)

    question = models.ForeignKey(Question, related_name="answers", verbose_name='Pregunta', on_delete=models.CASCADE)
    author = models.ForeignKey(get_user_model(), related_name="answers", verbose_name='Autor', on_delete=models.CASCADE)
    value = models.PositiveIntegerField("Respuesta", default=0)
    comment = models.TextField("Comentario", default="", blank=True)
    like_dislike = models.BooleanField(null=True)
