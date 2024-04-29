from django.db import models
import uuid
from django.utils.text import slugify
from django.db.models.signals import pre_save
from core.models import AuditableModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.crypto import get_random_string
from datetime import datetime, timezone
from core.models import AuditableModel

class Categories(models.Model):
    """ This entity would section the courses into their various categories"""
    icon = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name
    
    def get_all_category(self):
        return Categories.objects.all().order_by('id')
    

class Instrcutor(models.Model):
    """This table bears the information of the instructor"""
    instructor_profile = models.ImageField(upload_to='Media/author')
    name = models.CharField(max_length=200, null=True)
    instructor_bio = models.TextField()

    def __str__(self) -> str:
        return self.name
    
class Language(models.Model):
    """A table for the choice of language"""
    language = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.language
    

class Course(models.Model):
    """The course entity has module and lessons under it"""
    course_id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    title = models.CharField(max_length=500)
    description = models.TextField()
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE,null=True)
    image_content = models.ImageField(upload_to="Media/featured_img",null=True)
    video_content = models.CharField(max_length=300,null=True)
    instructor_profile = models.ForeignKey(Instrcutor,on_delete=models.CASCADE,null=True)
    deadline = models.CharField(max_length=100, null=True)
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)
    certificate = models.CharField(max_length=100,null=True)

    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("course_details", kwargs={'slug':self.slug})
    
def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    slug_url_by_id =  Course.objects.filter(slug=slug).order_by('-id')
    exists = slug_url_by_id.exists()
    if exists:
        new_slug = "%s-%s" % (slug, slug_url_by_id.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender,instance,*args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, Course)

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    module_name = models.CharField(max_length=200)
    start_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.module_name
    
class Lessons(models.Model):
    lesson_name = models.CharField(max_length=200)
    module_name = models.ForeignKey(Module, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.lesson_name
    
class Video(models.Model):
    video_id = models.IntegerField(null=True)
    thumbnail = models.ImageField(upload_to="Media/Yt_Thumbnail",null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson_name = models.ForeignKey(Lessons,on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    time_duration = models.IntegerField(null=True)
    preview = models.BooleanField(default=False)

    
    


    



    

