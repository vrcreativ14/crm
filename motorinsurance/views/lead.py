import datetime

from django.template import Context, Template
from django.http.response import JsonResponse
from dateutil.relativedelta import relativedelta
from django.views.generic import FormView, TemplateView

from motorinsurance.forms import MotorInsuranceLeadForm
from motorinsurance.models import Lead
from motorinsurance.tasks import create_deal_from_lead
from motorinsurance_shared.models import CarMake, CarTrim


class MotorInsuranceLeadFormView(FormView):
    form_class = MotorInsuranceLeadForm
    template_name = 'motorinsurance/lead/lead_form.djhtml'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        ctx['user_id'] = self.kwargs.get('user_id', 0)

        return ctx

    def get_form_kwargs(self):
        kwargs = super(MotorInsuranceLeadFormView, self).get_form_kwargs()
        kwargs['initial'] = {
            'year': self.request.GET.get('year', ''),
            'vehicle_insured_value': self.request.GET.get('value', ''),
            'value': self.request.GET.get('value', ''),
            'name': self.request.GET.get('name', ''),
            'contact_number': self.request.GET.get('phone', ''),
            'email': self.request.GET.get('email', '')
        }

        return kwargs

    def get_vehicle_make(self, make):
        if make:
            obj = CarMake.objects.filter(name__icontains=make)

            return obj[0].id if obj.count() else ''

    def yearsago(self, years):
        return datetime.datetime.now() - relativedelta(years=int(years))

    def form_invalid(self, form):
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    def form_valid(self, form):
        data = form.cleaned_data

        new_lead = Lead(
            company=self.request.company,

            lead_type=data["lead_type"],
            current_insurer=data["current_insurer"],
            current_insurance_type=data["current_insurance_type"],

            name=data["name"],
            email=data["email"],
            contact_number=data["contact_number"],
            dob=data["age"],
            nationality=data["nationality"],

            car_year=data["car_year"],

            date_of_first_registration=data["date_of_first_registration"],
            place_of_registration=data["place_of_registration"],
            first_license_country=data["first_license_country"],
            first_license_age=data["first_license_age"],
            uae_license_age=data["uae_license_age"],

            vehicle_insured_value=data["vehicle_insured_value"],

            years_without_claim=data["years_without_claim"],
            claim_certificate_available=data["claim_certificate_available"],

            private_car=data["private_car"],
            car_unmodified=data["car_unmodified"],
            car_gcc_spec=data["car_gcc_spec"],
        )

        if data.get('car_make'):
            new_lead.car_make = CarMake.objects.get(id=data['car_make'])

        if len(self.request.GET):
            new_lead.meta_info = {
                'utm_source': self.request.GET.get('utm_source'),
                'utm_medium': self.request.GET.get('utm_medium'),
                'utm_campaign': self.request.GET.get('utm_campaign')
            }

        if self.request.POST.get('cant_find_car'):
            new_lead.custom_car_name = "{} (Custom)".format(data['custom_car_name'])
        else:
            car_trim_id = data["car_model"]
            car_trim = CarTrim.objects.get(pk=car_trim_id)
            new_lead.car_trim = car_trim

        new_lead.save()

        deal = create_deal_from_lead(new_lead, data)

        car_model = ''
        car_body_type = ''

        if deal.car_trim:
            car_model = deal.car_trim.model.name
            car_body_type = deal.car_trim.algo_driven_data.get('body', '')

        response = {
            'success': True,
            'lead_id': new_lead.pk,

            'source': 'e-commerce',
            'deal_id': deal.pk,

            'client_email': deal.customer.email,
            'client_email_hash': deal.customer.get_email_hash(),

            'vehicle_model_year': deal.car_year,
            'vehicle_make': deal.car_make.name,
            'vehicle_model': car_model,
            'vehicle_body_type': car_body_type,
            'vehicle_sum_insured': deal.vehicle_insured_value,

            'client_nationality': deal.customer.get_nationality_display(),
            'client_gender': deal.customer.get_gender_display(),
            'client_age': deal.customer.get_age()
        }

        return JsonResponse(response)


class LeadSubmittedThanksView(TemplateView):
    template_name = "motorinsurance/lead/lead_submitted_thanks.djhtml"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_name = None
        custom_page_content = None

        if 'lead_id' in self.request.GET:
            try:
                lead = Lead.objects.get(
                    pk=self.request.GET['lead_id'],
                    company=self.request.company
                )
                user_name = lead.name
                ctx['user_name'] = user_name

            except Lead.DoesNotExist:
                pass

        if self.request.company.companysettings.motor_lead_form_thankyou_content:
            template = Template(self.request.company.companysettings.motor_lead_form_thankyou_content)
            context = Context({
                'user_name': user_name,
                'company_phone': self.request.company.companysettings.phone,
                'company_website': self.request.company.companysettings.website,
            })
            custom_page_content = template.render(context)

        ctx['custom_page_content'] = custom_page_content

        return ctx
