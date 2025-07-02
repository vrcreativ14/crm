import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse, HttpResponseNotFound, \
    HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.views import View

from core.help_scout import HelpScoutApi
from motorinsurance.models import Deal


class HelpScoutMixin:
    def has_access_to_helpscout(self, company):
        company_settings = company.companysettings
        for field_name in ['helpscout_client_id', 'helpscout_client_secret', 'helpscout_mailbox_id']:
            if not getattr(company_settings, field_name):
                return False

        return True

    def get_helpscout_api(self, company):
        assert self.has_access_to_helpscout(company)

        company_settings = company.companysettings

        mailbox_id = company_settings.helpscout_mailbox_id
        client_id = company_settings.helpscout_client_id
        client_secret = company_settings.helpscout_client_secret

        hs_api = HelpScoutApi(mailbox_id)
        hs_api.authenticate(client_id, client_secret)

        return hs_api


class HelpScoutConversationsView(HelpScoutMixin, LoginRequiredMixin, View):
    def transform_helpscout_conversations(self, conversations):
        summary_of_conversations = []

        for conv in conversations:
            created_by_title = '{} {} ({})'.format(conv['createdBy']['first'], conv['createdBy']['first'],
                                                   conv['createdBy']['type'])
            created_at = conv['createdAt']
            if created_at:
                created_at = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%Sz').strftime('%b %d, %Y')

            summary_of_conversations.append({
                'id': conv['id'],
                'created_by': created_by_title,
                'subject': conv['subject'],
                'created_at': created_at,
                'preview': conv['preview'],
                'web_link': conv['_links']['web']['href']
            })

        return summary_of_conversations

    def get(self, request, deal_id):
        if not self.has_access_to_helpscout(request.company):
            return HttpResponseBadRequest('You have not configured your Help Scout integration settings yet.')

        deal = get_object_or_404(Deal, pk=deal_id)
        if deal.company != request.company:
            return HttpResponseForbidden('You do not have access to this item')

        customer = deal.customer
        email = customer.email

        if not email:
            return JsonResponse({'message': 'No email set for the customer.', 'conversations': []})

        hs_api = self.get_helpscout_api(request.company)
        conversations = hs_api.get_conversations_for_email_address(email)
        if conversations is None:
            return HttpResponseServerError('Unable to get conversations for the deal\'s customer')

        conversations_summaries = self.transform_helpscout_conversations(conversations)

        return JsonResponse({'conversations': conversations_summaries})


class HelpScoutThreadsView(HelpScoutMixin, LoginRequiredMixin, View):
    def get_conversation_by_id(self, conversations, id_to_find):
        for conv in conversations:
            if conv['id'] == id_to_find:
                return conv

        return None

    def transform_helpscout_threads(self, threads):
        threads_summaries = []

        for thread in threads:
            if thread['type'] not in ['message', 'customer']:
                continue

            created_by_title = '{} {} ({})'.format(thread['createdBy']['first'], thread['createdBy']['first'],
                                                   thread['createdBy']['type'])

            created_at = thread['createdAt']
            if created_at:
                created_at = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%Sz').strftime('%b %d, %Y')

            body = thread['body']

            threads_summaries.append({
                'id': thread['id'],
                'created_at': created_at,
                'created_by': created_by_title,
                'body': body
            })

        return threads_summaries

    def get(self, request, deal_id, conversation_id):
        if not self.has_access_to_helpscout(request.company):
            return HttpResponseBadRequest('You have not configured your Help Scout integration settings yet.')

        deal = get_object_or_404(Deal, pk=deal_id)
        if deal.company != request.company:
            return HttpResponseForbidden('You do not have access to this item')

        customer = deal.customer
        email = customer.email

        if not email:
            return JsonResponse({'message': 'No email set for the customer.', 'conversations': []})

        hs_api = self.get_helpscout_api(request.company)
        conversations = hs_api.get_conversations_for_email_address(email)
        if self.get_conversation_by_id(conversations, conversation_id) is None:
            return HttpResponseNotFound('No conversation with this ID exists for this deal\'s customer')

        threads = hs_api.get_threads_for_conversation(conversation_id)
        if threads is None:
            return HttpResponseServerError('Unable to get threads for the deal\'s customer and this conversation id')

        return JsonResponse(self.transform_helpscout_threads(threads), safe=False)
