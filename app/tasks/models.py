from django.db import models
import uuid
import random
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import pre_save
from core.models import AuditableModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.crypto import get_random_string
from datetime import datetime, timezone
from django.template.defaultfilters import slugify
from core.models import AuditableModel
#from taggit.managers import TaggableManager
from django.utils.translation import gettext_lazy as _
#from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase

class Quiz(AuditableModel):
    module = models.OneToOneField("lms.Module",related_name="module_task",on_delete=models.CASCADE,blank=True,null=True)
    task = models.CharField(max_length=255)
    creator = models.ForeignKey("user.User",related_name='created_tasks',on_delete=models.CASCADE)
    reattempt = models.BooleanField(default=True,verbose_name='Reattempt Question')
    slug = models.SlugField(null=True, blank=True)


    class Meta:
        verbose_name = "Tasks"
        ordering = ['id','module']

    @property
    def task_count(self):
        """Determine the number of tasks taken by each user"""
        return self.task.count() 
    
    def __str__(self) -> str:
        return (self.task)
    
    #@property
    #def all_tags(self):
        #"""contains all the tags of this task"""
        #return [i.name for i in self.tags.all()]
    
    @property
    def attempters(self):
        """The number of users that attempted the task"""
        return self.task_score.count()
    
    
    @property
    def question_count(self):
        """Number of questions in the task"""
        return self.task_question.count()
    
    def task_attempters(self):
        return self.task_score.all()
    
    def get_absolute_url(self):
        return reverse('task:tasks',kwargs={'slug':self.slug})
    
    def save(self, *args,**kwargs):
        self.slug = slugify(self.task)
        super(Quiz,self).save(*args,**kwargs)


class MultipleChoiceQuestions(models.Model):
    """This model saves the multiple choice questions,
    options and the correct options"""
    quiz = models.ForeignKey(Quiz,related_name='questions',on_delete=models.CASCADE)
    prompt_question = models.CharField(max_length=225,blank=True,null=True)
    has_audio = models.BooleanField(default=False)
    recorded_audio_question = models.FileField(storage='audio-questions/',blank=True,null=True)

    class Meta:
        ordering = ['id']

    def __str__(self) -> str:
        return f'{self.prompt_question}'

class Answer(AuditableModel):
    question = models.ForeignKey(MultipleChoiceQuestions,related_name='question_answer',on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    has_audio =models.BooleanField(default=False)
    audio_record_answer = models.FileField(storage='audio-answers/',blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.text}'
    

    def __str__(self) -> str:
        return f'{self.text}'
    
class UserAttemptActivity(AuditableModel):
    """Presents the performance of each user
    that completed a task"""
    user = models.ForeignKey('user.User',on_delete=models.CASCADE,related_name='task_performance')
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name='task_performance')
    score = models.FloatField()
    date_taken = models.DateTimeField(auto_now_add=True)
    percentage_score = models.FloatField(default=0.0)

    def __str__(self) -> str:
        return f'{self.quiz.task} - {self.user}'
    def __str__(self) -> str:
        return f"{self.user}, you scored {self.score} in {self.quiz.task}"
    
class TheoryQuiz(AuditableModel):
    module = models.OneToOneField("lms.Course",related_name="module_quiz",on_delete=models.CASCADE,blank=True,null=True)
    quiz_name = models.CharField(max_length=255)
    created_by = models.ForeignKey("user.User",related_name="created_quiz",on_delete=models.CASCADE)
    question = models.TextField()

class TheoryQuizAttempt(AuditableModel):
    user =models.ForeignKey("user.User", on_delete=models.CASCADE,related_name='taken_quiz')
    theory_quiz = models.ForeignKey(TheoryQuiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.FloatField()
    date_taken = models.DateTimeField(auto_now_add=True)
    percentage_score = models.FloatField(default=0.00)
    submitted_answer = models.FileField()
    




    





