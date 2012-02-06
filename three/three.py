"""
A new Python wrapper for interacting with the Open311 API.
"""

import os
from collections import defaultdict
from itertools import ifilter

import requests
import simplejson as json


class Three(object):
    """The main class for interacting with the Open311 API."""

    def __init__(self, endpoint=None, **kwargs):
        keywords = defaultdict(str)
        keywords.update(kwargs)
        if endpoint:
            endpoint = self._configure_endpoint(endpoint)
            keywords['endpoint'] = endpoint
        self._keywords = keywords
        self.configure()

    def _global_api_key(self):
        """
        If a global Open311 API key is available as an environment variable,
        then it will be used when querying.
        """
        if 'OPEN311_API_KEY' in os.environ:
            api_key = os.environ['OPEN311_API_KEY']
        else:
            api_key = ''
        return api_key

    def configure(self, **kwargs):
        """Configure a previously initialized instance of the class."""
        keywords = self._keywords.copy()
        keywords.update(kwargs)
        if 'endpoint' in kwargs:
            endpoint = kwargs['endpoint']
            keywords['endpoint'] = self._configure_endpoint(endpoint)
        self.api_key = keywords['api_key'] or self._global_api_key()
        self.endpoint = keywords['endpoint']
        self.format = keywords['format'] or 'json'
        self.jurisdiction = keywords['jurisdiction']
        self.proxy = keywords['proxy']

    def _configure_endpoint(self, endpoint):
        """Configure the endpoint with a schema and end slash."""
        if not endpoint.startswith('http'):
            endpoint = 'https://' + endpoint
        if not endpoint.endswith('/'):
            endpoint += '/'
        return endpoint

    def reset(self):
        """Reset the class back to the original keywords and values."""
        self.configure()

    def _create_path(self, *args):
        """Create URL path for endpoint and args."""
        args = ifilter(None, args)
        path = self.endpoint + '/'.join(args) + '.%s' % (self.format)
        return path

    def get(self, *args, **kwargs):
        """Perform a get request."""
        url = self._create_path(*args)
        # TODO: Still need to add on additional parameters.
        data = requests.get(url, params=kwargs).content
        return data

    def discovery(self, url=None):
        """
        Retrieve the standard discovery file that provides routing
        information.

        >>> Three().discovery()
        {'discovery': 'data'}
        """
        if url:
            data = requests.get(url).content
        else:
            data = self.get('discovery')
        return data

    def services(self, code=None, **kwargs):
        """
        Retrieve information about available services. You can also enter a
        specific service code argument.

        >>> Three().services()
        {'all': {'service_code': 'data'}}
        >>> Three().services('033')
        {'033': {'service_code': 'data'}}
        """
        data = self.get('services', code, **kwargs)
        return data

    def requests(self, code=None, **kwargs):
        """
        Retrieve open requests. You can also enter a specific service code
        argument.

        >>> Three('api.city.gov').requests()
        {'all': {'requests': 'data'}}
        >>> Three('api.city.gov').requests('123')
        {'123': {'requests': 'data'}}
        """
        if code:
            kwargs['service_code'] = code
        data = self.get('requests', **kwargs)
        return data

    def request(self, id, **kwargs):
        """
        Retrieve a specific request using its service code ID.

        >>> Three('api.city.gov').request('12345')
        {'request': {'service_code': {'12345': 'data'}}}
        """
        data = self.get('requests', id, **kwargs)
        return data

    def convert(self, content):
        """Convert content to Python data structures."""
        if self.format == 'json':
            data = json.loads(content)
        else:
            # XML2Dict the content?
            data = content
        return data
