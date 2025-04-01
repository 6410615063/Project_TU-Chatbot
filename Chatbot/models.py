from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# - make profile model
# 	- detail
# 		link 1 to 1 with user
# 		have a list of conversations
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile') # for when connecting to Django's user model
    pass

# - make conversation model
# 	- detail
# 		have a list of chats between user & assistant
class Chat(models.Model):
    name = models.CharField(max_length=255)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='chats')
    # Profile obj can refer to this by 'obj.conversations.All()'
    messages = models.JSONField() # can just assign the list of dicts to this?