from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http.response import JsonResponse
from django.urls import reverse
from django.views.generic import View, DetailView

from motorinsurance.forms import PolicyForm
from motorinsurance.models import Deal
from motorinsurance.models import Policy
from core.models import Attachment

from core.docparser import DOCParser
from motorinsurance.constants import INSURANCE_TYPE_COMPREHENSIVE, INSURANCE_TYPE_TPL


class DealPolicyBaseView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = ('auth.create_motor_policies', 'auth.update_motor_policies')
    model = Deal

    def get_parser_id_for_insurer(self):
        deal = self.get_object()
        order = deal.get_order()

        if order:
            insurer_name = order.selected_product.product.insurer.name.lower()
            parser = DOCParser()
            return parser.get_parser_id_for_insurer(insurer_name)

        return False

    def get_allowed_insurers(self):
        return DOCParser.get_allowed_insurers_message()


class DealPolicyDocumentParserView(DealPolicyBaseView):
    def post(self, request, *args, **kwargs):
        data = {'success': False}

        parser_id = self.get_parser_id_for_insurer()

        if parser_id:
            parser = DOCParser()
            file = request.FILES.get('policy_document', None)

            response = parser.upload_document(parser_id, file)

            if response.status_code == 200:
                data = {
                    'success': True,
                    'url': reverse(
                        'motorinsurance:document-parsed-values',
                        kwargs={'parser_id': parser_id, 'document_id': response.json()['id']})
                }
            else:
                data['message'] = response.json()
        else:
            data['message'] = 'Cannot scan document for this insurer'

        return JsonResponse(data, safe=False)


class DealCanScanPolicyDocumentView(DealPolicyBaseView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'success': True if self.get_parser_id_for_insurer() else False,
            'allowed_insurers': self.get_allowed_insurers()
        }, safe=False)


class DealPolicyDocumentParsedValuesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        parser_id = kwargs['parser_id']
        document_id = kwargs['document_id']

        response = DOCParser().get_document(parser_id, document_id)

        if response.status_code == 200:
            doc = response.json()[0]

            policy_start_date = doc.get('start_date')
            policy_end_date = doc.get('end_date')

            # Sometimes DocParser can return a list of values for the parsed dates (not sure why). This handles that
            # case. See sentry issue FELIX-WEB-APP-89
            if policy_start_date:
                try:
                    policy_start_date = policy_start_date['formatted']
                except TypeError:
                    policy_start_date = None

            if policy_end_date:
                try:
                    policy_end_date = policy_end_date['formatted']
                except TypeError:
                    policy_end_date = None

            data = {
                'success': True,
                'policy_start_date': policy_start_date,
                'policy_end_date': policy_end_date,
                'policy_number': doc.get('policy_number'),
                'invoice_number': doc.get('invoice_number')
            }
        else:
            data = {
                'success': False,
                'message': response.json()['error']
            }

        return JsonResponse(data, safe=False)


class DealAddEditPolicyView(DealPolicyBaseView):
    def post(self, request, *args, **kwargs):
        deal = self.get_object()

        form_kwargs = {
            'data': request.POST,
            'files': request.FILES,
            'company': self.request.company
        }
        creating = True
        try:
            form_kwargs['instance'] = deal.policy
            creating = False
        except Policy.DoesNotExist:
            pass

        form = PolicyForm(**form_kwargs)

        if form.is_valid():
            policy = form.save(commit=False)
            policy.deal = deal
            policy.customer = deal.customer
            policy.company = self.request.company

            if creating:
                order = deal.get_order()
                selected_quoted_product = order.selected_product
                policy.product = selected_quoted_product.product

                policy.car_year = deal.car_year
                policy.car_make = deal.car_make
                policy.car_trim = deal.car_trim
                policy.custom_car_name = deal.custom_car_name
                policy.insurance_type = INSURANCE_TYPE_TPL if order.selected_product.product.is_tpl_product else INSURANCE_TYPE_COMPREHENSIVE

                policy.agency_repair = selected_quoted_product.agency_repair
                policy.ncd_required = selected_quoted_product.ncd_required

                policy.premium = order.payment_amount
                policy.deductible = selected_quoted_product.deductible
                policy.deductible_extras = selected_quoted_product.deductible_extras
                policy.insured_car_value = selected_quoted_product.insured_car_value
                policy.mortgage_by = order.mortgage_by

                policy.default_add_ons = selected_quoted_product.default_add_ons
                policy.paid_add_ons = order.selected_add_ons

                policy.owner = deal.producer

                deal.stage = Deal.STAGE_HOUSEKEEPING

                # No need to trigger algolia update from deals save
                # as it will trigger when the policy save method will be called below
                deal.save(user=self.request.user, no_algolia_update=True)

            policy.save(user=self.request.user)

            uploaded_documents = self.upload_other_documents(policy)

            policy_data = {
                'product': policy.product.name,
                'insurer': policy.product.insurer.name,
                'cover': 'TPL' if policy.product.is_tpl_product else 'comprehensive'
            }

            return JsonResponse({'success': True, 'creating': creating, 'policy': policy_data})
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })

    def upload_other_documents(self, policy):
        uploaded_documents = []
        other_documents = self.request.FILES.getlist('other_documents[]')

        if len(other_documents):
            for file in other_documents:
                attachment = Attachment(company=self.request.company, attached_to=policy)
                attachment.label = file.name
                attachment.added_by = self.request.user
                attachment.file = file
                attachment.save()

                uploaded_documents.append(attachment.get_file_url())

        return uploaded_documents
