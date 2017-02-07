"""
The Mailgun client
"""
import logging
import requests


logger = logging.getLogger(__name__)


class MailgunError(Exception):
    """ Base class for all Mailgun error. """
    pass


class MailgunCredentialsError(MailgunError):
    """
    Exception to be raised in case the provided credentials are invalid.
    """
    pass


class MailgunDomainError(MailgunError):
    """
    Exception to be raised in case the provided domain in not available.
    """
    pass


class Client(object):
    """ The client for Mailgun's API

    @param key: The API key.
    @param domain: The domain to send mails from.
    @param sanbox: Whether to use the sanbox domain in case the domain is not
    provided.
    """

    def __init__(self, key, domain=None, sandbox=False):
        self._CACHE = {}  # Internal REST API response cache
        self.api_key = key
        if not domain:
            domain = self.guess_domain(sandbox=sandbox)
        self.check_domain(domain)
        self.domain = domain

    def check_domain(self, domain):
        """
        Check whether the provided domain in valid.

        @param domain: The domain to check for.
        """
        domains = [d['name'] for d in self.domains(use_cache=True).get('items')]
        if domain not in domains:
            raise MailgunDomainError(
                'Invalid domain {}. Available domains: {}'.format(
                    domain, ', '.join(domains)
                ))

    def domains(self, use_cache=False):
        """
        Get all available domains.

        @param use_cache: Whether to use the internal caching system.
        """
        return self.__request('get', 'domains', use_cache=use_cache)

    def guess_domain(self, sandbox=False):
        """
        Guess the domain to use.
        If there is only one domain defined, use it.
        If there are more than one use the first "custom" one (ie. the first
        one that is not a sandboxed domain).
        If there are only sandboxed domains, return the first one.

        @param sandbox: Whether to use the first sandboxed domain.
        """
        domains = self.domains(use_cache=True).get('items')
        if not sandbox:
            # Skip this part if the user requested a sandboxed domain.
            custom_domains = [d for d in domains if d['type'] == 'custom']
            if len(custom_domains) > 0:
                return custom_domains[0]['name']
        sandboxed_domains = [d for d in domains if d['type'] == 'sandbox']
        if len(sandboxed_domains) > 0:
            return sandboxed_domains[0]['name']

    def __request(self, method, path, data=None, files=None, use_cache=False):
        """ Abstract request to Mailgun's REST API

        @param method: HTTP method to use (GET, POST, PUT, DELETE)
        @param path: REST path to use (last part of the URL)
        @param data: Optional data to be sent along the request.
        @param files: Files to be sent with the request.
        @param use_cache: Whether to use the internal caching system.
        @return: The JSON response from Mailgun's API
        """
        cache_index = '{} {} - {};{}'.format(method, path, data, files)
        if use_cache:
            if cache_index in self._CACHE:
                logger.debug('Cache hit for index "{}"'.format(cache_index))
                return self._CACHE[cache_index]
        url = 'https://api.mailgun.net/v2/{}'.format(path)
        auth = ('api', self.api_key)
        resp = requests.request(method, url, data=data, auth=auth, files=files)
        if resp.status_code == 401:
            raise MailgunCredentialsError('Invalid credentials')
        # Raise other possible errors
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise MailgunError(e)
        json_resp = resp.json()
        self._CACHE[cache_index] = json_resp
        return json_resp

    def send_mail(self, sender, to, subject, text, html=None, cc=None, bcc=None,
                  files=None):
        """ Sends an email using the mailgun API

        @param sender: sender's email address
        @param to: email address or list of email addresses to send the email to
        @param cc: email address or list of email addresses to put in cc
        @param bcc: email address or list of email addresses to put in bcc
        @param subject: email's subject
        @param text: email's plain text content
        @param html: email's html content
        @param files: list of file paths to put in attachment
        @return: the mailgun's API response
        """
        data = {'from': sender, 'to': to, 'subject': subject, 'text': text}
        if html:
            data['html'] = html

        if cc:
            data['cc'] = cc
        if bcc:
            data['bcc'] = bcc

        attached_files = []
        if files:
            if not isinstance(files, list):
                files = [files]
            for f in files:
                attached_files.append(('attachment', open(f, 'rb')))

        # Do not use the caching system here. Otherwise dupplicate messages
        # won't be sent.
        return self.__request('post', '{}/{}'.format(self.domain, 'messages'),
                              data=data, files=attached_files, use_cache=False)
