import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin

class ModelBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cedula = models.CharField(verbose_name='cedula o dni', max_length=13, blank=True, null=True, unique=True)
    email = models.EmailField('email address',unique=True)
    phone = models.CharField('Telefono',max_length=50,blank=True,null=True)
    
    objects = CustomUserManager()
    USERNAME_FIELD='email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name='user'
        verbose_name_plural='users'
        unique_together = ('username', 'email', 'cedula')
        
    def __str__(self, *args, **kwargs):
        return '{}'.format(self.username)
