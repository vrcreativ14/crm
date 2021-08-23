import json
import logging
import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import JsonResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.views import View
from django.views.generic import TemplateView

from auto_quoter.aman import AmanApiAutoQuoter
from auto_quoter.api_mappings.dat import models as dat_car_models
from auto_quoter.constants import TOKIO_MARINE_API, AMAN_API
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.mixins import CompanyAutoQuotationAllowedMixin
from auto_quoter.models import AutoQuoterConfig
from auto_quoter.oic import OICAutoQuoter
from auto_quoter.qic import QICAutoQuoter
from core.utils import add_empty_choice
from insurers.models import Insurer
from motorinsurance.forms.insurers import SalamaForm, NewIndiaForm, QICForm, OICForm, TokioMarineForm, UICForm, \
    InsuranceHouseForm, AmanForm, WataniaForm, AmanApiForm
from motorinsurance.models import Deal


class AutoQuoteView(LoginRequiredMixin, PermissionRequiredMixin, CompanyAutoQuotationAllowedMixin, TemplateView):
    template_name = 'motorinsurance/auto_quote_product_forms/generic_form.djhtml'
    permission_required = 'auth.create_motor_quotes'

    def get_deal(self):
        return Deal.objects.get(pk=self.kwargs['pk'])

    def get_insurer(self):
        return Insurer.objects.get(pk=self.kwargs['insurer_pk'])

    def get_form_klass(self):
        insurer = self.get_insurer()

        # This is done because for the Tokio Marine and AMAN insurance, we have 2 types of integrations, one with our
        # custom ratebook and another with their API. Our system assumes only 1 type of integration per insurer (which
        # is how it will be once we remove one of these integrations). These checks here are a temporary solution until
        # we can remove one of the two competing integrations.

        TokioMarineActiveForm = TokioMarineForm
        if insurer.name.lower() == 'tokio marine insurance':
            try:
                AutoQuoterConfig.objects.get(company=self.request.company, insurer=TOKIO_MARINE_API).get_options_dict()
                TokioMarineActiveForm = TokioMarineAPIForm
            except AutoQuoterConfig.DoesNotExist:
                pass

        AmanActiveForm = AmanForm
        if insurer.name.lower() == 'aman insurance':
            try:
                AutoQuoterConfig.objects.get(company=self.request.company, insurer=AMAN_API).get_options_dict()
                AmanActiveForm = AmanApiForm
            except AutoQuoterConfig.DoesNotExist:
                pass

        form_klass = {
            'salama takaful insurance': SalamaForm,
            'new india insurance': NewIndiaForm,
            'qatar insurance': QICForm,
            'oman insurance': OICForm,
            'tokio marine insurance': TokioMarineActiveForm,
            'union insurance': UICForm,
            'insurance house': InsuranceHouseForm,
            'aman insurance': AmanActiveForm,
            'watania insurance': WataniaForm,
        }[insurer.name.lower()]

        return form_klass

    def get_form(self):
        insurer = self.get_insurer()
        form_klass = self.get_form_klass()

        if hasattr(form_klass, 'template_name'):
            template_name = form_klass.template_name
        else:
            template_name = 'motorinsurance/auto_quote_product_forms/{}.djhtml'.format(insurer.name.lower())

        try:
            if get_template(template_name):
                self.template_name = template_name
        except TemplateDoesNotExist:
            pass

        deal = self.get_deal()
        if self.request.method == 'POST':
            form = form_klass(deal, self.request.POST)
        else:
            form = form_klass(deal)

        return self.add_missing_fields_to_form(form)

    def add_missing_fields_to_form(self, form):
        deal = self.get_deal()

        auto_quoter = form.auto_quoter()

        missing_fields = auto_quoter.deal_missing_fields(deal)
        for field in missing_fields:
            form.fields[field['name']] = field['field']

        return form

    def get_context_data(self, **kwargs):
        ctx = super(AutoQuoteView, self).get_context_data(**kwargs)
        ctx['deal'] = self.get_deal()
        ctx['form'] = self.get_form()

        return ctx

    def post(self, request, *args, **kwargs):
        insurer = self.get_insurer()
        deal = self.get_deal()
        form = self.get_form()

        if form.is_valid():
            auto_quoter = form.auto_quoter()

            deal = self.update_deals_extra_fields(form)

            try:
                responses = auto_quoter.get_quote_for_insurer_with_deal(insurer, deal, form.cleaned_data)
            except AutoQuoterException as e:
                responses = [{
                    'name': insurer.name,
                    'exception': True,
                    'message': str(e)
                }]

            # Enrich response with product info
            cleaned_responses = []
            for quote_response in responses:
                if quote_response.get('exception'):
                    cleaned_responses.append(quote_response)
                    continue

                product_code = quote_response['productCode']
                try:
                    product = request.company.available_motor_insurance_products.get(code=product_code)
                except ObjectDoesNotExist:
                    log = logging.getLogger('auto_quote')
                    log.warning('Auto quoter for %s returned a product code %s that is not available to company %d',
                                insurer.name, product_code, deal.company.pk)
                    continue
                else:
                    cleaned_responses.append(quote_response)

                quote_response['pk'] = product.pk
                quote_response['name'] = product.name
                quote_response['logo'] = product.get_logo()
                quote_response['ncd'] = quote_response.get('ncd') or False
                quote_response['currency'] = self.request.company.companysettings.get_currency_display()

            response = {'success': True, 'quotes': cleaned_responses}
        else:
            response = {'success': False, 'form_errors': form.errors}

        return JsonResponse(response, safe=False)

    def update_deals_extra_fields(self, form):
        deal = self.get_deal()
        delimiter = '___'

        for field, value in form.cleaned_data.items():
            if delimiter in field:
                v = field.split(delimiter)

                model_name = v[0]
                field_name = v[1]

                if model_name == 'deal':
                    model = deal
                elif model_name == 'quote':
                    model = deal.quote
                elif model_name == 'order':
                    model = deal.get_order()
                elif model_name == 'customer':
                    model = deal.customer
                elif model_name == 'customer_profile':
                    model = deal.customer.motorinsurancecustomerprofile

                setattr(model, field_name, value)
                model.save()

        return deal


class OICMMTTree(LoginRequiredMixin, PermissionRequiredMixin, CompanyAutoQuotationAllowedMixin, View):
    permission_required = ('auth.create_motor_quotes',)

    def get(self, request, *args, **kwargs):
        tree_level = request.GET['type']

        auto_quoter = OICAutoQuoter()
        auto_quoter.setup_for_company(request.company)

        if tree_level == 'specifications':
            model_id = request.GET['model_id']
            specs = auto_quoter.get_car_specs_for_model(model_id)

            response_list = [
                (s['id'], s['description']) for s in specs
            ]
        elif tree_level == 'vehicles':
            spec_id = request.GET['specification_id']
            vehicles = auto_quoter.get_vehicles_for_spec(spec_id)

            response_list = vehicles
        else:
            return JsonResponse({'success': False, 'error': f'{tree_level} is not a recognized MMT type option'})

        return JsonResponse({'response': response_list})


class DATMMTTree(LoginRequiredMixin, PermissionRequiredMixin, CompanyAutoQuotationAllowedMixin, View):
    permission_required = ('auth.create_motor_quotes',)

    def get(self, request, *args, **kwargs):
        make_id = request.GET.get('make_id')

        if not make_id:
            return JsonResponse({'success': False, 'error': f'Invalid Make ID'})

        choices = list(dat_car_models.get_model_choices_for_make_id(make_id))

        return JsonResponse({'response': choices})


class TokioMarineMMTTree(LoginRequiredMixin, PermissionRequiredMixin, CompanyAutoQuotationAllowedMixin, View):
    permission_required = ('auth.create_motor_quotes',)

    def get(self, request, *args, **kwargs):
        options = None
        tree_level = request.GET['level']
        deal_id = request.GET['deal_id']

        try:
            deal = Deal.objects.get(pk=deal_id, company=request.company)
        except Deal.DoesNotExist:
            return JsonResponse({'response': None, 'message': 'Deal not found.'})

        aq = TokioMarineApiAutoQuoter()
        aq.setup_for_company(deal.company)
        aq.login()

        if tree_level == 'model':
            options = aq.get_vehicle_model_choices_list(request.GET['make'])
        elif tree_level == 'make':
            options = aq.get_vehicle_make_choices_list()
        elif tree_level == 'trim':
            try:
                options = aq.api_response_to_choices(
                    aq.get_trims(deal.car_year,
                                 request.GET['make'],
                                 request.GET['model'],
                                 request.GET['body_type']))
            except AutoQuoterException as e:
                return JsonResponse({'response': None, 'message': str(e)})

        elif tree_level == 'engine_size':
            try:
                options = aq.api_response_to_choices(
                    aq.get_engine_sizes(deal.car_year,
                                        request.GET['make'],
                                        request.GET['model'],
                                        request.GET['trim'],
                                        request.GET['body_type']))
            except AutoQuoterException as e:
                return JsonResponse({'response': None, 'message': str(e)})

        elif tree_level == 'transmission':
            try:
                options = aq.api_response_to_choices(
                    aq.get_transmissions(deal.car_year,
                                         request.GET['make'],
                                         request.GET['model'],
                                         request.GET['trim'],
                                         request.GET['body_type'],
                                         request.GET['engine_size']))
            except AutoQuoterException as e:
                return JsonResponse({'response': None, 'message': str(e)})

        elif tree_level == 'region':
            try:
                options = aq.api_response_to_choices(
                    aq.get_regions(deal.car_year,
                                   request.GET['make'],
                                   request.GET['model'],
                                   request.GET['trim'],
                                   request.GET['body_type'],
                                   request.GET['engine_size'],
                                   request.GET['transmission']))
            except AutoQuoterException as e:
                return JsonResponse({'response': None, 'message': str(e)})

        if options:
            return JsonResponse({'response': add_empty_choice(options)})

        return JsonResponse({'response': None, 'message': 'Unknown value for parameter: level'})


class AmanApiVehicleInfoView(LoginRequiredMixin, PermissionRequiredMixin, CompanyAutoQuotationAllowedMixin, View):
    permission_required = ('auth.create_motor_quotes',)

    def get_deal(self):
        return Deal.objects.get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        deal = self.get_deal()

        auto_quoter = AmanApiAutoQuoter()
        auto_quoter.setup_for_company(deal.company)

        chassis_info_response = auto_quoter.get_vehicle_details(kwargs['chassis_number'])
        return JsonResponse(chassis_info_response)


class AmanApiDiscountsInfoView(LoginRequiredMixin, PermissionRequiredMixin, CompanyAutoQuotationAllowedMixin, View):
    permission_required = ('auth.create_motor_quotes',)

    def get_deal(self):
        return Deal.objects.get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        deal = self.get_deal()

        auto_quoter = AmanApiAutoQuoter()
        auto_quoter.setup_for_company(deal.company)

        discounts = auto_quoter.get_discounts()
        return JsonResponse([('', 'No Discount')] + discounts, safe=False)


class QICApiVehicleInfoView(LoginRequiredMixin, PermissionRequiredMixin, CompanyAutoQuotationAllowedMixin, View):
    permission_required = ('auth.create_motor_quotes',)

    def get_vehicle_info_from_api(self, deal, chassis_number):
        """Returns a tuple for the Vehicle Info received from the QIC API. Tuple data format is given below.

        If success: True, (make code, model code, year code)
        If failure: False, error message"""
        auto_quoter = QICAutoQuoter()
        try:
            vehicle_info = auto_quoter.get_vehicle_info(deal, chassis_number)
            return True, (vehicle_info['make'], vehicle_info['model'], vehicle_info['year'])
        except AutoQuoterException as e:
            return False, str(e)

    def get(self, request, deal_pk):
        deal = get_object_or_404(Deal, pk=deal_pk)

        chassis_number = request.GET['chassisNumber']

        api_response = self.get_vehicle_info_from_api(deal, chassis_number)
        if api_response[0]:
            return JsonResponse({
                "makeCode": api_response[1][0],
                "modelCode": api_response[1][1],
                "yearCode": api_response[1][2],
            })
        else:
            return HttpResponseServerError(api_response[1])


class QICApiTrimsView(LoginRequiredMixin, PermissionRequiredMixin, CompanyAutoQuotationAllowedMixin, View):
    permission_required = ('auth.create_motor_quotes',)

    def get_trims_from_api(self, deal, chassis_number, make_code, model_code, year_code):
        """Returns a tuple for the trims received from the QIC API. Tuple data format is given below.

        If success: True, [{"trimCode": 1, "title": ""}, ...]
        If failure: False, error message"""
        try:
            auto_quoter = QICAutoQuoter()
            trims = auto_quoter.get_trims(deal, chassis_number, make_code, model_code, year_code)
            return True, [
                {
                    "trimCode": trim['admeId'],
                    "title": trim['description']
                } for trim in trims
            ]
        except AutoQuoterException as e:
            return False, str(e)

    def get(self, request, deal_pk):
        deal = get_object_or_404(Deal, pk=deal_pk)

        chassis_number = request.GET['chassisNumber']
        make_code = request.GET['makeCode']
        model_code = request.GET['modelCode']
        year_code = request.GET['yearCode']

        api_response = self.get_trims_from_api(deal, chassis_number, make_code, model_code, year_code)
        if api_response[0]:
            return JsonResponse({
                "trims": api_response[1]
            })
        else:
            return HttpResponseServerError(api_response[1])


class QICApiTrimDetailsView(LoginRequiredMixin, PermissionRequiredMixin, CompanyAutoQuotationAllowedMixin, View):
    permission_required = ('auth.create_motor_quotes',)

    def get_vehicle_info_form_api(self, deal, chassis_number, make_code, model_code, year_code, trim_code):
        """Returns a tuple for the vehicle info received from the QIC API. Tuple data format is given below.

        If success: True, <VEHICLE INFO>
        If failure: False, error message"""
        try:
            auto_quoter = QICAutoQuoter()
            vehicle_data = auto_quoter.get_vehicle_details(deal, chassis_number, make_code, model_code, year_code,
                                                           trim_code)
            return True, {
                "bodyTypeCode": vehicle_data['bodyType'],
                "makeCode": vehicle_data['vehMake'],
                "modelCode": vehicle_data['vehModel'],
                "modelYear": vehicle_data['modelYear'],
                "isGccSpec": vehicle_data['gccSpecYn'] == '1',
                "value": vehicle_data['vehicleValue'],
                "cylinders": vehicle_data['cylinders'],
                "seats": vehicle_data['seats'],
                "trimCode": vehicle_data['admeId']
            }
        except AutoQuoterException as e:
            return False, str(e)

    def get(self, request, deal_pk):
        deal = get_object_or_404(Deal, pk=deal_pk)

        chassis_number = request.GET['chassisNumber']
        make_code = request.GET['makeCode']
        model_code = request.GET['modelCode']
        year_code = request.GET['yearCode']
        trim_code = request.GET['trimCode']

        api_response = self.get_vehicle_info_form_api(deal, chassis_number, make_code, model_code, year_code, trim_code)
        if api_response[0]:
            return JsonResponse(api_response[1])
        else:
            return HttpResponseServerError(api_response[1])


class QICApiGetQuotesView(LoginRequiredMixin, PermissionRequiredMixin, CompanyAutoQuotationAllowedMixin, View):
    permission_required = ('auth.create_motor_quotes',)

    def get_quotes(self, deal, name, make_code, model_code, model_year, sum_insured, vehicle_type_code,
                   vehicle_usage_code, number_cylinders, nationality_code, seating_capacity, first_registration_date,
                   gcc_spec, previous_insurance_valid, is_total_loss, driver_dob, no_claim_years,
                   no_claim_years_self_dec, chassis_number, driver_gcc_experience, trim_code):
        auto_quoter = QICAutoQuoter()

        try:
            quote_response = auto_quoter.get_quote(deal, name, make_code, model_code, model_year, sum_insured,
                                                   vehicle_type_code,
                                                   vehicle_usage_code, number_cylinders, nationality_code,
                                                   seating_capacity, first_registration_date,
                                                   gcc_spec, previous_insurance_valid, is_total_loss, driver_dob,
                                                   no_claim_years,
                                                   no_claim_years_self_dec, chassis_number, driver_gcc_experience,
                                                   trim_code)
            return True, quote_response
        except AutoQuoterException as e:
            return False, str(e)

    def post(self, request, deal_pk):
        deal = get_object_or_404(Deal, pk=deal_pk)

        request_data = json.loads(request.body)

        api_response = self.get_quotes(
            deal,
            request_data['name'],
            request_data['makeCode'],
            request_data['modelCode'],
            request_data['modelYear'],
            request_data['sumInsured'],
            request_data['vehicleType'],
            request_data['vehicleUsage'],
            request_data['numberOfCylinders'],
            request_data['nationality'],
            request_data['seatingCapacity'],
            datetime.datetime.strptime(request_data['firstRegistrationDate'], '%Y-%m-%d'),
            '1' if request_data['isGccSpec'] else '0',
            '1' if request_data['isPreviousInsuranceValid'] else '0',
            '1' if request_data['isTotalLoss'] else '0',
            datetime.datetime.strptime(request_data['driverDOB'], '%Y-%m-%d'),
            request_data['noClaimYears'],
            request_data['noClaimYearsSelfDec'],
            request_data['chassisNumber'],
            request_data['gulfDrivingExperience'],
            request_data['trimCode']
        )
        if api_response[0]:
            responses = api_response[1]

            # Enrich response with product info
            cleaned_responses = []
            for quote_response in responses:
                if quote_response.get('exception'):
                    cleaned_responses.append(quote_response)
                    continue

                product_code = quote_response['productCode']
                try:
                    product = request.company.available_motor_insurance_products.get(code=product_code)
                except ObjectDoesNotExist:
                    log = logging.getLogger('auto_quote')
                    log.warning('Auto quoter for %s returned a product code %s that is not available to company %d',
                                'QIC', product_code, deal.company.pk)
                    continue
                else:
                    cleaned_responses.append(quote_response)

                quote_response['pk'] = product.pk
                quote_response['name'] = product.name
                quote_response['logo'] = product.get_logo()
                quote_response['ncd'] = quote_response.get('ncd') or False
                quote_response['currency'] = self.request.company.companysettings.get_currency_display()

            return JsonResponse({'quotes': cleaned_responses})
        else:
            return HttpResponseServerError(api_response[1])