from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser,PermissionsMixin)


# Create your models here.

user_types = (
                ("staff","staff"),
                ("owner","owner"),
                ('other','other')
                )

class UserManager(BaseUserManager):
    def create_user(self,phone_number, full_name='null',
                    user_type="staff",email=None,
                    api_number= None,
                    password=None):
        if not phone_number:
            raise ValueError('Users must have a phone number')
        if email:
            email =self.normalize_email(email)
        user = self.model(phone_number=phone_number,
                          full_name=full_name,
                          user_type=user_type,
                          email=email
                           )
        user.set_password(password)
        user.save(using=self._db)
        return user 
  
    def create_superuser(self, phone_number, password):
        user = self.create_user(phone_number,password=password,
                                full_name="SITE CREATOR",user_type='other')
        user.is_admin = True
        user.staff=True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser,PermissionsMixin):
    full_name = models.CharField(verbose_name='full_name', max_length=255)
    phone_number = models.CharField(verbose_name='phone number', max_length=20,unique=True)
    user_type = models.CharField(max_length=20, choices = user_types,default='staff')
    email = models.EmailField(verbose_name='email address',max_length=255,null=True,
                              blank=True,unique=True)
    api_number = models.CharField(verbose_name='api_number', max_length=20,
                                  blank=True,null=True)
    verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    staff=models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone_number'
    
    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        if not self.is_admin and self.staff:
            if perm =="Users.add_user" or perm=="Users.change_user" or perm=="Users.delete_user":
                return False
            else:
                return True
        else:
            return True

    # remember to set appropriate permissions.
    def has_module_perms(self, app_label):
        if not self.is_admin and self.staff:
            if app_label =="knox" or app_label=="auth" :
                return False
            else:
                return True
        else:
            return True
    @property

    def is_staff(self):
        return self.staff
    

class Customer(models.Model):
    """Model definition for Customer."""

    # TODO: Define fields here
    full_name = models.CharField(max_length=255,unique=True)
    phone_number = models.CharField(max_length=20,unique=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    balance = models.FloatField(default=0.0,blank=True)
    address = models.TextField(null=True, blank=True)


    class Meta:
        """Meta definition for Customer."""

        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        """Unicode representation of Customer."""
        return self.full_name


class Payee(models.Model):
    """Model definition for Payee."""

    # TODO: Define fields here
    name = models.CharField(max_length=255,unique=True)
    phone_number = models.CharField(max_length=20,unique=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    class Meta:
        """Meta definition for Payee."""

        verbose_name = 'Payee'
        verbose_name_plural = 'Payees'

    def __str__(self):
        """Unicode representation of Payee."""
        return self.name

   