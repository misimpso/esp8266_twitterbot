from parse_json import ParseJson
import random
import socket
import ssl

try:
    import ubinascii as binascii
    import ujson as json
    import ure as re
    import utime as time

    from uhashlib import sha1
    from urequests import request
except:
    import binascii
    import json
    import re
    import time

    from hashlib import sha1
    from requests import request
    

class oauth_request:
    SHA1_BLOCK_SIZE = 64
    percent_validate = re.compile("[A-Za-z0-9-_.~]")
    http_status_regex = re.compile("HTTP/1.1 ([{\d}]+) ([A-Z-z0-9 ]+)\\r\\n")

    @classmethod
    def get(cls, *args, **kwargs):
        """ Send authenticated `GET` request.
        """
        return cls.__send_request("GET", *args, **kwargs)

    @classmethod
    def post(cls, *args, **kwargs):
        """ Send authenticated `POST` request.
        """
        return cls.__send_request("POST", *args, **kwargs)

    @classmethod
    def __send_request_old(cls, method, url, params, key_ring):
        """ Send an OAuth 1.0 authenticated request to given `url`.
        
        Args:
            method (string, GET|POST): Request type.
            url (string): URL to send request to.
            params (dict): Dictionary of parameters to append to URL.
            key_ring (dict): API credentials for authentication.
        
        Returns:
            Request's response.
        """
        method = method.upper()
        auth_header = cls.__create_auth_header(method, url, params, **key_ring)
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        url += "?{}".format(
            "&".join([
                "{}={}".format(*map(cls.__percent_encode, map(str, item)))
                for item in params.items()
            ]))
        return request(method=method, url=url, headers=headers)

    @classmethod
    def __send_request(cls, method, url, params, key_ring, filter_map):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        protocol, _, host, path = url.split("/", 3)
        path += "?{}".format(
            "&".join([
                "{}={}".format(*map(cls.__percent_encode, map(str, item)))
                for item in params.items()]))
        
        if protocol == "http:":
            addr = socket.getaddrinfo(host, 80)[0][-1]
            sock.connect(addr)
        elif protocol == "https:":
            addr = socket.getaddrinfo(host, 443)[0][-1]
            sock.connect(addr)
            sock = ssl.wrap_socket(sock)

        packet = [
            "{} /{} HTTP/1.1".format(method, path),
            "Accept: */*",
            "Connection: close",
            "User-Agent: Python/0.1",
            "Content-Length: 0",
            "Content-Type: application/x-www-form-urlencoded",
            "Authorization: {}".format(cls.__create_auth_header(method, url, params, **key_ring)),
            "Host: {}".format(host),
            "\n"
        ]
        packet = b"\r\n".join(map(str.encode, packet))

        sock.send(packet)
        del packet

        http_status_buffer = []
        status_byte = None
        while status_byte is not "\n":
            status_byte = sock.recv(1).decode()
            http_status_buffer.append(status_byte)
        http_status_buffer = "".join(http_status_buffer)
        http_status = cls.http_status_regex.findall(http_status_buffer)
        if len(http_status):
            http_status = http_status[0]
            print(http_status)
        else:
            print("HTTP status not found. [{}]".format(http_status_buffer))
            return

        if http_status[0] == '200':
            while True:
                return_header_buffer = []
                rh_byte = None
                while rh_byte is not "\n":
                    rh_byte = sock.recv(1).decode()
                    return_header_buffer.append(rh_byte)
                return_header_buffer = "".join(return_header_buffer)
                if return_header_buffer == "\r\n":
                    break
            
            json_data = []
            while True:
                data = sock.recv(1024).decode()
                if data:
                    json_data.appen(data)
                else:
                    break

            json_data = json.loads("".join(json_data))
            sock.close()
            return json_data

        sock.close()
        return http_status

    @classmethod
    def __create_auth_header(cls, method, url, data, consumer_key, consumer_secret, access_token, access_token_secret):
        """ Build OAuth header authentication string.
            https://developer.twitter.com/en/docs/basics/authentication/oauth-1-0a/authorizing-a-request
        """
        oauth = {
            "oauth_consumer_key": consumer_key,
            "oauth_nonce": cls.__generate_nonce(),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": int(time.time()), # 946684800 + time.time(),
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

        signing_key = "&".join([consumer_secret, access_token_secret])
        sanitized_oauth["oauth_signature"] = cls.__percent_encode(
            cls.__generate_hmac(signing_key, signature_base_string))
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
        return binascii.b2a_base64(hmac).decode()[:-1]

    @classmethod
    def __percent_encode(cls, dirty_string):
        """ Substitue characters in the given `dirty_string` that aren't in the regex
            `[A-Za-z0-9-_.~]` with their hexadecimal unicode code point.
        """
        dirty_list = list(dirty_string)
        for d_i, dirty_item in enumerate(dirty_list):
            if not cls.percent_validate.match(dirty_item):
                dirty_list[d_i] = "%{:X}".format(ord(dirty_item))
        return "".join(dirty_list)

    @classmethod
    def __generate_nonce(cls):
        """ Generate a 32 character, strictly alpha-numeric string.
        """
        if hasattr(time, 'ticks_us'):
            random.seed(time.ticks_us())
        else:
            random.seed(time.time())
        alpha_num = sum(map(list, (range(48, 58),range(65, 91), range(97, 123))), [])
        nonce = []
        for _ in range(32):
            rand_index = len(alpha_num)
            while rand_index >= len(alpha_num):
                rand_index = random.getrandbits(6)
            nonce.append(chr(alpha_num[rand_index]))
        return "".join(nonce)
