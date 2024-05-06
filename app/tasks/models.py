from django.db import models
import uuid
from django.utils.text import slugify
from django.db.models.signals import pre_save
from core.models import AuditableModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.crypto import get_random_string
from datetime import datetime, timezone
from core.models import AuditableModel

class Quiz(AuditableModel):
    module = models.OneToOneField("lms.Module",related_name="module_task",on_delete=models.CASCADE,blank=True,null=True)
    name_of_task = models.CharField(max_length=255)
    creator = models.ForeignKey("user.User",related_name='created_tasks',on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Tasks"
        ordering = ['id','module']

    @property
    def task_count(self):
        return self.task.count() 
    
    def __str__(self) -> str:
        return (self.name_of_task)



class MultipleChoiceTasks(models.Model):
    """This model saves the multiple choice questions,
    options and the correct options"""
    question = models.CharField(max_length=200,null=True)
    option_1 = models.CharField(max_length=200,null=True)
    option_2 = models.CharField(max_length=200, null=True)
    option_3 = models.CharField(max_length=200,null=True)
    option_4 = models.CharField(max_length=200)

