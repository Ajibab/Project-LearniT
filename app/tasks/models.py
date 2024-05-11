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

class RangeField(models.IntegerField):
    description = _("Integer field with range")
    def __init__(self,min_val,max_val,*args,**kwargs): 
        self.min_val=min_val
        self.max_val=max_val
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
    
        min_value=self.min_val
        max_value=self.max_val
        return super().formfield(**{
            'min_value': min_value,
            'max_value': max_value,
            **kwargs,
        })
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
 
        kwargs['min_val']=self.min_val
        kwargs['max_val']=self.max_val

        return name, path, args, kwargs     


    def rel_db_type(self, connection):
        print('yes here')
        if connection.features.related_fields_match_type:
            return self.db_type(connection)
        else:
            return models.IntegerField().db_type(connection=connection)

class QuizCategory(AuditableModel):
    module = models.OneToOneField("lms.Module",related_name="module_task",on_delete=models.CASCADE,blank=True,null=True)
    task = models.CharField(max_length=255)
    creator = models.ForeignKey("user.User",related_name='created_tasks',on_delete=models.CASCADE)
    user = models.ForeignKey('user.User',on_delete=models.CASCADE,related_name='user_quiz',blank=True,null=True)
    reattempt = models.BooleanField(default=True,verbose_name='Reattempt Question')
    #tags=TaggableManager(through=UUIDTaggedItem)
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
        super(QuizCategory,self).save(*args,**kwargs)


class SetOfQuestions(models.Model):
    """This model saves the multiple choice questions,
    options and the correct options"""
    tasks = models.ForeignKey('QuizCategory',on_delete=models.CASCADE,related_name='tasks_questions')
    slug = models.SlugField(null=True, blank=True, max_length=100)
    question = models.TextField (default='')#(max_length=200,blank=True,null=True)
    option_1 = models.CharField(max_length=1024,blank=True,null=True)
    option_2 = models.CharField(max_length=1024,blank=True,null=True)
    option_3 = models.CharField(max_length=1024,blank=True,null=True)
    option_4 = models.CharField(max_length=1024,blank=True,null=True)
    has_project = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=3,verbose_name='points')
    answer = RangeField(min_val=1,max_val=4,default=1,verbose_name='correct option')
    project = models.FileField(storage='project-questions/',blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.question}'
    
    def get_answers(self):
        multiple_choice_answer = list(Answer.objects.filter(question=self))
        data = []
        random.shuffle(multiple_choice_answer)
        for choices in multiple_choice_answer:
            data.append({
                'answer': choices.answer,
                'is_correct': choices.is_correct
            })
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.question[:60])
        super(SetOfQuestions,self).save(*args,**kwargs)

class Answer(AuditableModel):
    question = models.ForeignKey(SetOfQuestions,related_name='question_answer',on_delete=models.CASCADE)
    text = models.CharField(max_length=1025)
    is_correct =models.BooleanField(default=False)
    has_project = models.BooleanField(default=False)
    project_solution_upload = models.FileField(storage='project-solution',blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.text}'
    
class QuizPerformance(AuditableModel):
    """Presents the performance of each user
    that completed a task"""
    user = models.ForeignKey('user.User',on_delete=models.CASCADE,related_name='task_performance')
    quiz = models.ForeignKey(QuizCategory,on_delete=models.CASCADE,related_name='task_performance')
    score = models.FloatField()
    percentage_score = models.FloatField(default=0.0)

    def __str__(self) -> str:
        return f'{self.quiz.task} - {self.user}'
    def __str__(self) -> str:
        return f"{self.user}, you scored {self.score} in {self.quiz.task}"




    





