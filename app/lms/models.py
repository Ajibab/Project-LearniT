from django.db import models
import calendar
import uuid
from django.utils.text import slugify
from django.db.models.signals import pre_save
from core.models import AuditableModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.crypto import get_random_string
from datetime import datetime, timezone
from core.models import AuditableModel

"""Define the choice field for course duration in months
using the calender module"""
MONTH_DURATION_CHOICES = [(str(i), calendar.month_name[i]) for i in range(1,13)] 

##--- Define Tables ---##
class Categories(models.Model):
    """ This entity would section the courses into their various categories"""
    icon = models.ImageField(upload_to='Media/author')
    name = models.CharField(max_length=200)
    # You wont be able to create Categories if icon is not provided
    # since null&blank is not set to True, is that the desired behavior?

    def __str__(self) -> str:
        return self.name
    
    def get_all_category(self):
        return Categories.objects.all().order_by('id')
    

    
class Language(models.Model):
    """A table for the choice of language"""
    language = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.language
    
class CourseCategory(models.Model):
    """This is an intermediary model that links the Course and Categories models.
    This was done to address the error thrown up due to the use of the many-to-many field"""
    course = models.ForeignKey("Course",on_delete=models.CASCADE)
    categories = models.ForeignKey(Categories,on_delete=models.CASCADE)

    # What is the error due to usage of ManytoMany?
    # We should define categories on Course as ManytoMany

class Course(models.Model):
    """The course entity has module and lessons under it"""
    course_id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    title = models.CharField(max_length=500)
    description = models.TextField()
    preview = models.BooleanField(default=False)
    timeline_number = models.IntegerField()
    timeline_duration_type = models.CharField(max_length=500, choices=MONTH_DURATION_CHOICES, default='1')
    categories = models.ManyToManyField(Categories,related_name="course",through=CourseCategory,through_fields=('course','categories'))
    language = models.ForeignKey(Language, on_delete=models.CASCADE,null=True)
    instructor_profile = models.ForeignKey('user.User',on_delete=models.CASCADE,null=True)
    slug = models.SlugField(unique=True, max_length=500)  
    certificate = models.CharField(max_length=100,null=True)  

    # certificate should be file field
    # use id instead of course_id
    # Have you read about signals ?
    
    def __str__(self) -> str:
        return self.title
    
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

    # Can we use name instead of module_name. Since we are on Module, when
    # we see name, we know it's for the module. Though in some cases,
    # we may need to do that to avoid naming collision
    
    def __str__(self) -> str:
        return self.module_name
    
class ModuleTasksSubmission(AuditableModel):
    module = models.ForeignKey(Module,on_delete=models.CASCADE,related_name='submitted_module_assignment')
    user = models.ForeignKey('user.User',on_delete=models.CASCADE,related_name='module_assignment_for_user')
    assignment_upload = models.FileField(upload_to='upload_file/',blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.user} {self.module}'
    

    
class Lessons(models.Model):
    lesson_name = models.CharField(max_length=200)
    module_name = models.ForeignKey(Module, on_delete=models.CASCADE) 
    content = models.TextField(max_length=300,null=True)  ## Rich text editor
    # use module instead of module_name
    # Let model name be singular i.e. Lesson not Lessons
    def __str__(self) -> str:
        return self.lesson_name 
    
class UserCourseActivityTracker(models.Model):
    user_name = models.ForeignKey('user.User',on_delete=models.CASCADE) #use user
    start_date = models.DateTimeField(auto_now=True) 
    end_date = models.DateTimeField(auto_now=True)  
    course = models.ForeignKey(Course,on_delete=models.CASCADE)  

    # auto_now_add=True set to now only when the obj is 1st created, does not update 
    # subsequently
    # auto_now=True update it to now everytime this obj is saved

    def __str__(self) -> str:
        return self.user_name
    
class UserCertificate(models.Model):
    user_name = models.ForeignKey('user.User', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE) #do you know the implication of
    certificate = models.CharField(max_length = 100, null=True)
    # use user as field name
    # certificate needsto be a filefield /uploas/certificate

    def __str__(self) -> str:
        return self.certificate


    


    



    

