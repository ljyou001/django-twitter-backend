from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

# from comments.models import Comment
from accounts.services import UserService
from likes.models import Like
from utils.time_helper import utc_now
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES


class Tweet(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, # In production, always use set_null for on delete
        null=True, 
        help_text='The user who posted this tweet',
    )
    # too long for one line? one line one parm, "," in the last line
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True) # auto_now_add only update while creating
    updated_at = models.DateTimeField(auto_now=True) # auto_now: update every time

    class Meta:
        index_together = (('user', 'created_at'),)
        # This way to create a compound index
        # There could be multiple compound indcies, so it is a tuple in a tuple
        # it is actually created a sorted table in DB with fields: ['user', 'created_at', 'id']
        # you need to make migration for the index
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        """
        return (datetime.datetime.now() - self.created_at).seconds / 3600
        """
        # TypeError: can't subtract offset-naive and offset-aware datetimes
        # This is because now() have no time zone. but created_at has time zone. 
        return (utc_now() - self.created_at).seconds / 3600
    
    # @property
    # def comments(self):
    #     """
    #     Obtain the comments of a tweet
    #     """
    #     return self.comment_set.all()
    #     # return Comment.objects.filter(tweet=self)

    @property
    def like_set(self):
        """
        Obtain all the like of a tweet
        """
        return Like.objects.filter(
            content_type = ContentType.objects.get_for_model(Tweet),
            object_id = self.id,
        ).order_by('-created_at')
    
    def __str__(self):
        """
        This function define the string representation while you print the instance
        """
        return f'{self.created_at} {self.user}: {self.content}'
    
    @property
    def cached_user(self):
        return UserService.get_user_through_cache(self.user_id)
    

class TweetPhoto(models.Model):
    """
    TweetPhoto model: Allow Tweets to have photos
    """
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    # The photo file belongs to which tweet
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # You can directly use tweet.user to know who the photo belongs to
    # Here we provided a better way to query
    # We can know who sent this photo directly rather than join two tables which could causing performance issue

    file = models.FileField()
    # Image file
    order = models.IntegerField(default=0)
    # The order of photo in a tweet

    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES, 
        # Why choices?
        # It means you can only choose the status defined by developer in TWEET_PHOTO_STATUS_CHOICES
    )
    # The status of the photo, 
    # In censorship use case, it could be 0: pending, 1: approved, 2: rejected
    # Why IntegerField?
    # Because we did not match the number to a certain string, 
    # If you want to change your expected status, it will be very convenient

    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    # soft delete mark: when a image is deleted, it will only be marked as deleted
    # It will only be removed from the bucket after a certain time
    # Why?
    # 1. Immediate delete will causing performance issue, 
    #    here we can use some async tasks to delete in the background,
    #    rather than slowing down the production service
    # 2. Recycle mechanism, admins can still see the file

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('tweet', 'order'),
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('has_deleted', 'deleted_at'),
            ('status', 'created_at'),
        )

    def __str__(self):
        return f'{self.created_at} {self.tweet_id}: {self.user} {self.file}'