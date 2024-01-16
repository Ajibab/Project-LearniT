from django.db import models

class User(models.Model):
    Id = models.UUIDField(blank=False)
    first_name = models.CharField(max_length=40, null=False, blank=False)
    surname = models.CharField(max_length=40, null=False, blank=False)
    occupation = models.CharField(max_length=40)
    email = models.EmailField(unique=True, null=False, blank=False)
    phone_number = models.IntegerField()
    country = models.CharField(max_length=50)
    user_password = models.IntegerField(blank=False)
    user_time_in = models.DateField()
    interests = models.TextField(max_length=40)

class Pending_user(models.Model):
    pending_user_email = models.EmailField(null=False,blank=False,unique=True)

class User_Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField()
    digital_resume = models.FileField()

class Token(models.Model):
    user_name = User.email
    password = models.IntegerField()

