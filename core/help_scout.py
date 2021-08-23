import logging

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


class HelpScoutApi:
    def __init__(self, mailbox_id):
        self.log = logging.getLogger('api.helpscout')

        self.mailbox_id = mailbox_id
        self.session = None

        self.api_base = 'https://api.helpscout.net/v2/'

    def authenticate(self, client_id, client_secret):
        self.log.info('HelpScoutApi: Logging in with client id %s', client_id)

        client = BackendApplicationClient(client_id)
        oauth_session = OAuth2Session(client=client)
        oauth_session.fetch_token('https://api.helpscout.net/v2/oauth2/token', client_secret=client_secret)

        self.session = oauth_session

    def get_all_embedded_items(self, starting_url, embedded_key, **kwargs):
        """Starting from the given URL, this method will get all items from HelpScout for the given query.

        It does so by first GETting the starting_url, extracting the embedded items (using the key provided) and then
        checking to see if there is a 'next' link in the '_links' key of the response from the HelpScout API.

        If a next link is found, this method starts the process again using the next link. Otherwise it returns the
        items collected so far.

        `starting_url`: The url to start from
        `embedded_key`: The key used to extract the required item type from the `_embedded` dictionary in the
            HS response
        `**kwargs`: Passed to the requests.GET method"""
        self.log.debug('HelpScoutApi: Trying to get all items of type %s, starting from URL: %s',
                       embedded_key, starting_url)

        api_response = self.session.get(starting_url, **kwargs)
        if api_response.status_code != requests.codes.ok:
            self.log.error('HelpScoutApi: Non-OK response code from API when trying to get %s. Code: %d',
                           embedded_key, api_response.status_code)
            return None

        response_data = api_response.json()

        items = []
        while True:
            if '_embedded' in response_data:
                items.extend(response_data['_embedded'][embedded_key])

            if 'next' in response_data['_links']:
                next_url = response_data['_links']['next']['href']
                self.log.debug('HelpScoutApi: Found next link in %s response: %s', embedded_key, next_url)

                api_response = self.session.get(next_url, **kwargs)
                if api_response.status_code != requests.codes.ok:
                    self.log.error('HelpScoutApi: Non-OK response code from API when trying to get %s. Code: %d',
                                   embedded_key, api_response.status_code)
                    return None

                response_data = api_response.json()
            else:
                break

        return items

    def get_conversations_for_email_address(self, email_address):
        self.log.debug('HelpScoutApi: Getting conversations for email address %s from mailbox id %s', email_address,
                       self.mailbox_id)

        query = f'email:{email_address}'
        params = {
            'mailbox': self.mailbox_id,
            'status': 'all',
            'query': query
        }

        return self.get_all_embedded_items(self.api_base + 'conversations', 'conversations', params=params)

    def get_threads_for_conversation(self, conversation_id):
        self.log.debug('HelpScoutApi: Getting threads for conversation id %s', conversation_id)
        url = self.api_base + 'conversations/' + str(conversation_id) + '/threads'

        return self.get_all_embedded_items(url, 'threads')
