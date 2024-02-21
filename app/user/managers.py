from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext as _ 
from .enums import SytemRoleEnum

class CustomUserManager(BaseUserManager):
    """
    Creating a Custom user model with email as the unique identifier
    
    """
    def create_user_with_email(self,email,**extra_fields):
        """ Create and save a User with the assigned username and password"""
        if not email:
            raise ValueError(_('Set email address'))
        user=self.model(email=email, is_active=True,
                        verified=True, roles=[SytemRoleEnum.CUSTOMER,],**extra_fields)
        user.save()
        return user


    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Set email address'))
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save()
        return user
    ##--Create a super user--##
    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get("is_staff",True) is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        user = self.create_user(email,password,**extra_fields)
        user.save()
    
