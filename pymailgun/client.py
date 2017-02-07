"""
The Mailgun client
"""
import requests


class MailgunCredentialsError(Exception):
    """
    Exception to be raised in case the provided credentials are invalid.
    """
    pass


class Client(object):
    """ The client for mailgun's API

    @param key: the api key
    @param domain: the domain to send mails from
    """

    def __init__(self, key, domain):
        self.api_key = key
        self.domain = domain
        self.check_credentials()

    def check_credentials(self):
        """ Check the provided credentials """
        resp = self.__request('get', 'domains')
        if resp.status_code == 401:
            raise MailgunCredentialsError('Invalid credentials')

    def __request(self, method, path, data=None, files=None):
        url = 'https://api.mailgun.net/v2/{}'.format(path)
        auth = ('api', self.api_key)
        return requests.request(method, url, data=data, auth=auth, files=files)

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

        if files and isinstance(files, list):
            attached_files = []
            for f in files:
                attached_files.append(('attachment', open(f)))
            return self.__request('post', self.domain, 'messages', data=data,
                                  files=attached_files)

        return self.__request('post', '{}/{}'.format(self.domain, 'messages'),
                              data=data)
