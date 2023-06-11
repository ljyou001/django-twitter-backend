from testing.testcases import TestCase

LIKE_BASE_URL = '/api/likes/'


class LikeAPITestCase(TestCase):
    def setUp(self):
        self.user1, self.client1 = self.create_user_and_client('user1')
        self.user2, self.client2 = self.create_user_and_client('user2')

    def test_tweet_like(self):
        tweet = self.create_tweet(self.user1)
        data = {'content_type': 'tweet', 'object_id': tweet.id}

        # Negative test: anonymous user can't like a tweet
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # Negative test: GET method is not allowed
        response = self.client1.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # Negative test: wrong spell of content_type
        response = self.client1.post(LIKE_BASE_URL, {
            'content_type': 'twitter', 
            'object_id': tweet.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # Negative test: wrong object id
        response = self.client1.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)
        print(response.data['errors'])
        self.assertEqual('object_id' in response.data['errors'], True)

        # Positive test: user1 can like a tweet
        response = self.client1.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        # Positive test: check duplicated like
        response = self.client1.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 1)
        response = self.client2.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_comment_like(self):
        tweet=self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)
        data = {'content_type': 'comment', 'object_id': comment.id}

        # Negative test: anonymous user can't like a comment
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # Negative test: GET method is not allowed
        response = self.client1.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # Negative test: wrong spell of content_type
        response = self.client1.post(LIKE_BASE_URL, {
            'content_type': 'coment', 
            'object_id': comment.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # Negative test: wrong object id
        response = self.client1.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id' in response.data['errors'], True)

        # Positive test: user1 can like a comment
        response = self.client1.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        # Positive test: check duplicated like
        response = self.client1.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 1)
        response = self.client2.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)
