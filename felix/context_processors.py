import hashlib
import hmac

from django.conf import settings

from accounts.models import CompanySettings
from core.utils import serialize_to_json
from felix.constants import GENDER_CHOICES, MARITAL_STATUS_LIST, EMIRATES_LIST
from motorinsurance.constants import LICENSE_AGE_LIST


def settings_processor(request):
    """Adds the settings as a variable to all templates"""
    cs = {}

    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        user_hash = hmac.new(
            bytes(settings.INTERCOM["SECRET_KEY"], encoding='utf-8'),
            bytes(str(request.user.id), encoding='utf-8'),
            digestmod=hashlib.sha256).hexdigest()

        company_settings = CompanySettings.objects.defer(
            'motor_email_content_lead_submitted',
            'motor_email_content_quote_generated',
            'motor_email_content_quote_updated',
            'motor_email_content_order_summary',
            'motor_email_content_policy_issued',
        ).get(company_id=settings.COMPANY_ID)

        cs = {
            'user': request.user,
            'user_hash': user_hash,
            'userprofile': request.user.userprofile,
            'is_admin': request.user.userprofile.has_admin_role(),
            'is_producer': request.user.userprofile.has_producer_role(),
            'company': request.company,
            'companysettings': request.company.companysettings,
            'company_subdomain': settings.DOMAIN,

            'emirates_list': serialize_to_json(EMIRATES_LIST),
            'license_age_list': serialize_to_json(LICENSE_AGE_LIST),
            'gender_list': serialize_to_json(GENDER_CHOICES),
            'marital_status_list': serialize_to_json(MARITAL_STATUS_LIST),

            'environment': settings.ENVIRONMENT,

            'algolia_env': settings.ALGOLIA['ENV'],
            'algolia_app_id': settings.ALGOLIA['APPLICATION_ID'],
            'algolia_search_api_key': settings.ALGOLIA['SEARCH_API_KEY'],

            'intercom_app_id': settings.INTERCOM['APP_ID'],

            'age_range': range(18, 99),
            'azure_storage_shared_token': settings.AZURE_STORAGE_SHARED_TOKEN
        }

    cs.update({
        'debug': settings.DEBUG,
        'amplitude_api_key': settings.AMPLITUDE['API_KEY']
    })

    return cs


def override_css(request):
    """Adds URL to override CSS file for the given company"""
    return {
        'override_css': f'public/css/override/{settings.DOMAIN}.css'
    }
