"""
Deprecated
use newsfeeds.models.hbase_newsfeed.HBaseNewsFeed instead
"""
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from newsfeeds.listeners import push_newsfeed_to_cache
from tweets.models import Tweet
from utils.memcached_helper import MemcachedHelper


class NewsFeed(models.Model):
    """
    It is a model for news feeds
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Note this user: it is not saying who sent the tweet, it is who can read the tweet
    # say if someone have 3 follower, it will show 3 newsfeeds with 3 different users
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        # We want the DB sorted by user, then created_at
        # Why user first? Because showing news feeds is based on logged-in user
        unique_together = (('user', 'tweet'),)
        # One user can only have one unique tweet once, no deplicate tweet for one user
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'
    
    # In this case, we don't need to cache the user
    # As the user is just used for query but not for display
    @property
    def cached_tweet(self):
        return MemcachedHelper.get_object_through_cache(Tweet, self.tweet_id)

post_save.connect(push_newsfeed_to_cache, sender=NewsFeed)