from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from tweets.models import Tweet

class TestCase(DjangoTestCase):
    
    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'a-generic-password'
        if email is None:
            email = f'{username}@twitter.com'
        return User.objects.create_user(username=username, email=email, password=password)
    
    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default content'
        return Tweet.objects.create(user=user, content=content)