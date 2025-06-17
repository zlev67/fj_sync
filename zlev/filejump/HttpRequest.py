from abc import ABCMeta, abstractmethod

import os
import zlib
import json
import base64
from urllib.parse import urlparse

from requests.auth import HTTPBasicAuth, AuthBase    # pylint: disable=E0401
import requests                                      # pylint: disable=E0401



class Auth(metaclass=ABCMeta):
    @abstractmethod
    def auth(self) -> AuthBase:
        """

        Returns:

        """


class BasicAuth(Auth):
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def auth(self):
        return HTTPBasicAuth(self.user, self.password)



class HttpRequest:
    # pylint: disable=R0913
    def __init__(self, url, *, auth=None, headers=None, verify=False, timeout=1000):
        """
        Create HTTP request sender

        :param url:
        :param auth:
        :param headers:
        :param verify:
        :param timeout:
        """
        self.url = url
        self.auth = auth
        self.verify = verify
        self.timeout = timeout
        if headers:
            self.headers = headers
        else:
            self.headers = {'Content-Type': 'application/json'}

    def put_request(self, data):
        """

        :param data:
        :return:
        """
        response = requests.put(
            self.url,
            auth=self.auth.auth() if self.auth is not None else None,
            headers=self.headers,
            data=data,
            verify=self.verify,
            timeout=self.timeout
        )
        return response

    def delete_request(self, data=None):
        """

        :return:
        """
        response = requests.delete(
            self.url,
            data=data,
            headers=self.headers,
            auth=self.auth.auth() if self.auth is not None else None,
            verify=self.verify,
            timeout=self.timeout
        )
        return response

    def get_request(self, data=None, params=None):
        """

        :param data:
        :param params:
        :return:
        """
        response = requests.get(
            self.url,
            headers=self.headers,
            data=data,
            auth=self.auth.auth() if self.auth is not None else None,
            params=params,
            verify=self.verify,
            allow_redirects=True,
            timeout=self.timeout
        )
        try:
            result = json_unzip(response.content)
            response._content = bytes(json.dumps(result), 'utf-8)')
        except Exception:  # pylint: disable=W0703
            pass
        return response

    def post_request(self, data=None, *, compress=False, files=None):
        """
        wrapper to requests.post

        :param data: data to post
        :param compress: indicates if data should be zipped on post
        :param files: possible stream posting (files)
        :return:
        """
        if compress and data:
            data = json_zip(data)
        response = requests.post(
            self.url,
            headers=self.headers,
            data=data,
            files=files,
            auth=self.auth.auth() if self.auth is not None else None,
            verify=self.verify,
            timeout=self.timeout
        )
        return response

