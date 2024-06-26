from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_delete, post_save

from comments.listeners import increase_comments_count, decrease_comments_count
from likes.models import Like
from tweets.models import Tweet
from utils.memcached_helper import MemcachedHelper
from utils.time_helper import utc_now


class Comment(models.Model):
    """
    In this version, we only archieve a easy comment feature:
    You can only comment one's tweet, but you cannot comment one's comment.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('tweet', 'created_at'),)
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return '{} - {} commented {} | on tweet ID {}'.format(
            self.created_at, 
            self.user, 
            self.content,
            self.tweet_id,
        )
    
    @property
    def like_set(self):
        return Like.objects.filter(
            content_type = ContentType.objects.get_for_model(Comment),
            object_id = self.id,
        ).order_by('-created_at')
    
    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)
    
    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds / 3600
    
pre_delete.connect(decrease_comments_count, sender=Comment)
post_save.connect(increase_comments_count, sender=Comment)