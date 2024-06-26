from django_hbase.models import EmptyColumnError, BadRowKeyError
from friendships.models import HBaseFollowing, HBaseFollower, Friendship
from friendships.services import FriendshipService
from testing.testcases import TestCase
import time


class FriendshipServiceTests(TestCase):

    def setUp(self):
        # super(FriendshipServiceTests, self).setUp()
        # # To ensure the setUp function in TestCase can be executed
        super(FriendshipServiceTests, self).setUp()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')

    def test_get_following(self):
        user3 = self.create_user('user3')
        user4 = self.create_user('user4')
        for to_user in [user3, user4, self.user2]:
            self.create_friendship(from_user=self.user1, to_user=to_user)

        user_id_set = FriendshipService.get_following_user_id_set(self.user1.id)
        self.assertEqual(user_id_set, {user3.id, user4.id, self.user2.id})

        FriendshipService.unfollow(self.user1.id, self.user2.id)
        user_id_set = FriendshipService.get_following_user_id_set(self.user1.id)
        self.assertEqual(user_id_set, {user3.id, user4.id})


class HBaseTests(TestCase):

    @property
    def ts_now(self):
        return int(time.time() * 1000000)
    
    def test_save_and_get(self):
        timestamp = self.ts_now
        following = HBaseFollowing(from_user_id=123, to_user_id=34, created_at=timestamp)
        following.save()

        instance = HBaseFollowing.get(from_user_id=123, created_at=timestamp)
        self.assertEqual(instance.from_user_id, 123)
        self.assertEqual(instance.to_user_id, 34)
        self.assertEqual(instance.created_at, timestamp)

        following.to_user_id = 456
        following.save()

        instance = HBaseFollowing.get(from_user_id=123, created_at=timestamp)
        self.assertEqual(instance.to_user_id, 456)

        instance = HBaseFollowing.get(from_user_id=123, created_at=self.ts_now)
        self.assertEqual(instance, None)

    def test_create_and_get(self):
        # Miss column data
        try:
            HBaseFollower.create(to_user_id=1, created_at=self.ts_now)
            exception_raised = False
        except EmptyColumnError:
            exception_raised = True
        self.assertEqual(exception_raised, True)

        # Invalid row key
        try:
            HBaseFollower.create(from_user_id=1, to_user_id=2)
            exception_raised = False
        except BadRowKeyError as e:
            exception_raised = True
            self.assertEqual(str(e), 'Missing row key: created_at')
        self.assertEqual(exception_raised, True)

        # Good data
        ts = self.ts_now
        HBaseFollower.create(from_user_id=1, to_user_id=2, created_at=ts)
        instance = HBaseFollower.get(to_user_id=2, created_at=ts)
        self.assertEqual(instance.from_user_id, 1)
        self.assertEqual(instance.to_user_id, 2)
        self.assertEqual(instance.created_at, ts)

        # Get Missing key
        try:
            HBaseFollower.get(to_user_id=2)
            exception_raised = False
        except BadRowKeyError as e:
            exception_raised = True
            self.assertEqual(str(e), 'Missing row key: created_at')
        self.assertEqual(exception_raised, True)

    def test_filter(self):
        HBaseFollowing.create(from_user_id=1, to_user_id=2, created_at=self.ts_now)
        HBaseFollowing.create(from_user_id=1, to_user_id=3, created_at=self.ts_now)
        HBaseFollowing.create(from_user_id=1, to_user_id=4, created_at=self.ts_now)

        following = HBaseFollowing.filter(prefix=(1, None))
        self.assertEqual(3, len(following))
        self.assertEqual(following[0].from_user_id, 1)
        self.assertEqual(following[0].to_user_id, 2)
        self.assertEqual(following[1].from_user_id, 1)
        self.assertEqual(following[1].to_user_id, 3)
        self.assertEqual(following[2].from_user_id, 1)
        self.assertEqual(following[2].to_user_id, 4)

        # Test limit
        results = HBaseFollowing.filter(prefix=(1, None), limit=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].to_user_id, 2)

        results = HBaseFollowing.filter(prefix=(1, None), limit=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].to_user_id, 2)
        self.assertEqual(results[1].to_user_id, 3)

        results = HBaseFollowing.filter(prefix=(1, None), limit=4)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].to_user_id, 2)
        self.assertEqual(results[1].to_user_id, 3)
        self.assertEqual(results[2].to_user_id, 4)

        results = HBaseFollowing.filter(start=(1, results[1].created_at), limit=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].to_user_id, 3)
        self.assertEqual(results[1].to_user_id, 4)

        # Test reverse
        results = HBaseFollowing.filter(prefix=(1,None), limit=2, reverse=True)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].to_user_id, 4)
        self.assertEqual(results[1].to_user_id, 3)

        results = HBaseFollowing.filter(start=(1, results[1].created_at), limit=2, reverse=True)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].to_user_id, 3)
        self.assertEqual(results[1].to_user_id, 2)