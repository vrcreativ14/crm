import json

from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.auto_quoter_base import AutoQuoterBase
from auto_quoter.models import AutoQuoterConfig, InsurerApiTransactionLog


class CustomRateBooksBase(AutoQuoterBase):
    """This is the base class for auto quotes that use the PHP based rate books API developed by Faisal (UpWork)."""
    api_url = None
    product_code_format_str = None
    insurer = None
    insurer_ratebook_name = None

    def __init__(self):
        super().__init__()

        self._vehicle_mapping_cache = None

    def license_age_choice_to_years(self, license_age_text):
        return {
            "less than 6 months": 0,
            "less than 1 year": 0,
            "less than 2 years": 1,
            "more than 2 years": 2,
        }.get(license_age_text, 0)

    def years_no_claims_choice_to_years(self, no_claims_text):
        return dict([
            ("unknown", 0),
            ("never", 0),
            ("this year", 0),
            ("last year", 1),
            ("2 years ago", 2),
            ("3 years ago", 3),
            ("4 years ago", 4),
            ("5 years or more", 5),
        ]).get(no_claims_text, 0)

    def setup_for_company(self, company):
        self.company = company

        try:
            self.config = AutoQuoterConfig.objects.get(company=company, insurer=self.insurer).get_options_dict()
        except AutoQuoterConfig.DoesNotExist:
            raise AutoQuoterException('The {} auto quoter is not configured'.format(self.insurer))

    def prepare_request_data(self, deal, form_data):
        customer = deal.customer
        customer_motorprofile = customer.motorinsurancecustomerprofile

        repair_types_allowed = 'agency,nonagency'

        return {
            "customer": {
                "nationality": customer.nationality,
                "gender": customer.gender,
                "date_of_birth": customer.dob.strftime('%Y-%m-%d') if customer.dob else '',
                "first_license_country": customer_motorprofile.first_license_country,
                "first_license_age": self.license_age_choice_to_years(customer_motorprofile.first_license_age),
                "uae_license_age": self.license_age_choice_to_years(customer_motorprofile.uae_license_age)
            },
            "deal": {
                "deal_type": deal.lead_type,
                "vehicle_type": form_data['vehicle_type'],
                "vehicle_passengers": deal.number_of_passengers,
                "car_year": deal.car_year,
                "car_make": deal.car_make.name,
                "car_model": deal.car_trim.model.name if deal.car_trim else '',
                "car_trim": deal.car_trim.title if deal.car_trim else '',
                "sum_insured": form_data['insured_value'],
                "current_cover": deal.current_insurance_type,
                "current_insurer": deal.current_insurer,
                "emirate_of_registration": deal.place_of_registration,
                "first_registration_date": deal.date_of_first_registration.strftime('%Y-%m-%d') if deal.date_of_first_registration else '',
                "years_without_claim": self.years_no_claims_choice_to_years(deal.years_without_claim),
                "no_claim_certificate_available": deal.claim_certificate_available,
                "private_vehicle": deal.private_car,
                "unmodified_vehicle": deal.car_unmodified,
                "gcc_spec_vehicle": deal.car_gcc_spec,
                "insurer": self.insurer_ratebook_name,
                "repair_condition_allowed": repair_types_allowed,
            }
        }

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        raise NotImplemented('Subclasses of CustomRateBooksBase must implement this method')

    def add_record_to_insurance_logs(self, deal, request_data, quotes_response):
        InsurerApiTransactionLog.objects.create(
            company=deal.company,
            insurer=self.insurer,
            deal=deal,
            request_content=json.dumps(request_data),
            response_info=quotes_response.status_code,
            response_content=quotes_response.text,
        )

    def get_deal_missing_data_fields(self, deal):
        missing_data_fields = []

        if not deal.date_of_first_registration:
            missing_data_fields.append('deal.date_of_first_registration')

        return missing_data_fields
