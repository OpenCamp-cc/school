from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from db.models import BaseModel, CreatedUpdatedMixin
from users.models import User


class ChoiceQuestion(BaseModel, CreatedUpdatedMixin):
    content = models.TextField()
    is_multiple_choice = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='choice_questions'
    )

    def __str__(self):
        return self.content[:50]


class QuestionOption(BaseModel, CreatedUpdatedMixin):
    question = models.ForeignKey(
        ChoiceQuestion, on_delete=models.CASCADE, related_name='options'
    )
    content = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.content


class TextQuestion(BaseModel, CreatedUpdatedMixin):
    content = models.TextField()
    answer = models.TextField()
    alternative_answers = models.JSONField(default=list)
    is_case_sensitive = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='text_questions'
    )

    def __str__(self):
        return self.content[:50]


class Quiz(BaseModel, CreatedUpdatedMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    due_date = models.DateTimeField(null=True, blank=True)
    is_auto_graded = models.BooleanField(default=True)
    end_message = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    allow_multiple_attempts = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class QuizChoiceQuestion(BaseModel, CreatedUpdatedMixin):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='choice_questions'
    )
    question = models.OneToOneField(
        ChoiceQuestion, on_delete=models.CASCADE, related_name='quiz_question'
    )
    order = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['order']


class QuizTextQuestion(BaseModel, CreatedUpdatedMixin):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='text_questions'
    )
    question = models.OneToOneField(
        TextQuestion, on_delete=models.CASCADE, related_name='quiz_question'
    )
    order = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['order']


class QuizAttempt(BaseModel, CreatedUpdatedMixin):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        null=True,
        blank=True,
    )
    visitor = models.ForeignKey(
        'Visitor',
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        null=True,
        blank=True,
    )
    score = models.FloatField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    attempt_number = models.PositiveSmallIntegerField(default=1)


class ChoiceQuestionSubmission(BaseModel, CreatedUpdatedMixin):
    quiz_attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name='choice_submissions'
    )
    question = models.ForeignKey(ChoiceQuestion, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(QuestionOption, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    feedback = models.TextField(blank=True)


class TextQuestionSubmission(BaseModel, CreatedUpdatedMixin):
    quiz_attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name='text_submissions'
    )
    question = models.ForeignKey(TextQuestion, on_delete=models.CASCADE)
    answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    feedback = models.TextField(blank=True)


class Visitor(BaseModel, CreatedUpdatedMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    extra_info = models.JSONField(default=dict, blank=True)
