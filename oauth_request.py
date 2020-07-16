import random
import ubinascii
import ujson as json
import ure as re
import urequests as requests
import utime as time

from uhashlib import sha1

class oauth_request:
    SHA1_BLOCK_SIZE = 64
    percent_validate = re.compile("[A-Za-z0-9-_.~]")

    @classmethod
    def post(cls, url, params, key_ring):
        """ Post method with OAuth 1.0
        """
        auth_header = cls.__create_auth_header("POST", url, params, **key_ring)
        print(auth_header)
        # return
        headers = {"Authorization": auth_header, "Context-Type": "application/x-www-form-urlencoded", "User-Agent": "OAuth gem v0.4.4"}
        url += "?{}".format(
            "&".join([
                "{}={}".format(cls.__percent_encode(str(k)), cls.__percent_encode(str(v)))
                for k, v in params.items()
            ]))
        print("URL : {}".format(url))
        return requests.post(url, headers=headers)

    @classmethod
    def __create_auth_header(cls, method, url, data, consumer_key, consumer_secret, access_token, access_token_secret):
        """ Build OAuth header authentication string.
            https://developer.twitter.com/en/docs/basics/authentication/oauth-1-0a/authorizing-a-request
        """
        oauth = {
            "include_entities": "true",
            "oauth_consumer_key": consumer_key,
            "oauth_nonce": "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg",  # cls.__generate_nonce(),  
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": 1318622958,  # 946684800 + time.time(),
            "oauth_token": access_token,
            "oauth_version": 1.0,
        }
        oauth.update(data)

        sanitized_oauth = {}
        flat_oauth = []
        for key in sorted(oauth):
            key = cls.__percent_encode(str(key))
            value = cls.__percent_encode(str(oauth[key]))
            flat_oauth.append("{}={}".format(key, value))
            if key != "include_entities":
                sanitized_oauth[key] = value
            

        [sanitized_oauth.pop(key) for key in data]

        signature_base_string = "&".join([
            method.upper(),
            cls.__percent_encode(url),                  
            cls.__percent_encode("&".join(flat_oauth))
        ])

        signing_key = "{}&{}".format(consumer_secret, access_token_secret)

        print("")
        print("Signing Key : {}".format(signing_key))
        print("Base String : {}".format(signature_base_string))
        print("")

        sanitized_oauth["oauth_signature"] = cls.__generate_hmac(signing_key, signature_base_string)
        return "OAuth {}".format(
            ", ".join([
                '{}="{}"'.format(key, sanitized_oauth[key])
                for key in sorted(sanitized_oauth)
            ]))

    @classmethod
    def __generate_hmac(cls, key, message):
        """ HMAC-SHA1 implementation
            https://github.com/python/cpython/blob/3.8/Lib/hmac.py
        """
        key = key.encode()
        message = message.encode()
        if len(key) > cls.SHA1_BLOCK_SIZE:
            key = sha1(key).digest()
        key += (b'\x00' * (cls.SHA1_BLOCK_SIZE - len(key)))
        outer, inner = sha1(), sha1()
        inner.update(bytes((x ^ 0x36) for x in key))
        outer.update(bytes((x ^ 0x5C) for x in key))
        inner.update(message)
        outer.update(inner.digest())
        hmac = outer.digest()
        return ubinascii.b2a_base64(hmac).decode()[:-1]

    @classmethod
    def __percent_encode(cls, dirty_string):
        dirty_list = list(dirty_string)
        for d_i, dirty_item in enumerate(dirty_list):
            if not cls.percent_validate.match(dirty_item):
                dirty_list[d_i] = "%{:X}".format(ord(dirty_item))
        return "".join(dirty_list)

    @classmethod
    def __generate_nonce(cls):
        random.seed(time.ticks_us())
        alpha_num = sum(map(list, (range(48, 58), range(65, 91), range(97, 123))), [])
        nonce = []
        for _ in range(32):
            rand_index = len(alpha_num)
            while rand_index >= len(alpha_num):
                rand_index = random.getrandbits(6)
            nonce.append(chr(alpha_num[rand_index]))
        return "".join(nonce)
