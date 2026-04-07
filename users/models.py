from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Pass for now, inherits username, email, password, etc.
    # is_staff flag acts as the admin indicator.
    pass
