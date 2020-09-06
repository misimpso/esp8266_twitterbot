from oauth_request import oauth_request

class Actions:

    search_string = "Retweet to win"

    urls = {
        "tweet": "https://api.twitter.com/1.1/statuses/update.json",
        "search_posts": "https://api.twitter.com/1.1/search/tweets.json",
        "follow": "https://api.twitter.com/1.1/friendships/create.json",
        "retweet": "https://api.twitter.com/1.1/statuses/retweet/:{}.json",
        "favorite": "https://api.twitter.com/1.1/favorites/create.json"
    }

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.key_ring = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "access_token": access_token,
            "access_token_secret": access_token_secret
        }
        self.next_action_time = 0

    @classmethod
    def check_ratelimit(cls, func):
        pass

    def search(self):
        filter_map = {
            "statuses": [{
                "full_text": True,
                "id": True,
                "entities": {
                    "user_mentions": [{
                        "screen_name": True
                    }]},
                "retweeted_status": {
                    "id": True,
                    "user": {
                        "screen_name": True
                    }
                },
                "user": {
                    "screen_name": True
                }
            }], "errors": True
        }
        # filter_map = None
        response = oauth_request.get(
            url=self.urls["search_posts"],
            params={
                "q": self.search_string,
                "result_type": "mixed",
                "tweet_mode": "extended",
                "count": 1,
                "format": "compact"
            },
            key_ring=self.key_ring,
            filter_map=filter_map
        )
        return response

    def follow(self, screen_name):
        response = oauth_request.post(
            url=self.urls["follow"],
            params={
                "screen_name": screen_name,
                "follow": "true"},
            key_ring=self.key_ring,
            filter_map={"errors": True}
        )
        return response

    def retweet(self, tweet_id):
        response = oauth_request.post(
            url=self.urls["retweet"].format(tweet_id),
            key_ring=self.key_ring,
            filter_map={"errors": True}
        )
        return response

    def favorite(self, tweet_id):
        response = oauth_request.post(
            url=self.urls["follow"],
            params={"id": tweet_id},
            key_ring=self.key_ring,
            filter_map={"errors": True}
        )
        return response

    def tweet(self, message):
        response = oauth_request.post(
            url=self.urls["tweet"],
            params={"status": message},
            key_ring=self.key_ring,
            filter_map={"errors": True}
        )
        print(response)