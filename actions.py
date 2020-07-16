from oauth_request import oauth_request

class Actions:

    urls = {
        "tweet": "https://api.twitter.com/1.1/statuses/update.json",
        "search_posts": "https://api.twitter.com/1.1/search/tweets.json",
    }

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.key_ring = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "access_token": access_token,
            "access_token_secret": access_token_secret
        }
        self.last_action_time = 0

    def follow(self):
        pass

    def tweet(self, message):
        url = self.urls["tweet"]
        params = {"status": message}
        response = oauth_request.post(url, params, self.key_ring)
        print(response.text)