from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class UserProfileModel(models.Model):


    # Create relationship (don't inherit from User!)
    user = models.OneToOneField(User,    on_delete=models.CASCADE)
    # Add any additional attributes you want can be defined below


    # Add any additional attributes you want
    # comment = models.CharField()

    def __str__(self):
        # Built-in attribute of django.contrib.auth.models.User !
        return self.user.username
