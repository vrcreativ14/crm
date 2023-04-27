
from enum import IntEnum
from healthinsurance.constants import *
from healthinsurance.models.quote import *
from healthinsurance.serializers import *
from django.http import JsonResponse
from collections import OrderedDict
from felix.constants import COUNTRIES
from django.template import Context
from django.template import Template

def deal_stages_to_number(argument):
    switcher = {
        STAGE_LOST : 0,
        STAGE_NEW : 1,
        STAGE_QUOTE : 2,
        STAGE_DOCUMENTS : 3,        
        STAGE_FINAL_QUOTE :4,
        STAGE_PAYMENT : 5,
        STAGE_POLICY_ISSUANCE: 6,
        STAGE_BASIC: 6.5,
        STAGE_HOUSE_KEEPING: 7,
        STAGE_WON: 8,
    }

    return switcher.get(argument.lower(), 0)

def sub_stages_to_number(**kwargs):
    stage = kwargs.get('stage')
    sub_stage = kwargs.get('sub_stage')
    if sub_stage == None:
        return 1
    if stage == STAGE_DOCUMENTS:
        switcher = {
            DOCUMENTS_RECEIVED: 1,
            WORLD_CHECK: 2,
            DOCUMENTS_SEND_TO_INSURER: 3            
        }
    elif stage == STAGE_BASIC:
        switcher = {
            BASIC_QUOTED:1,
            BASIC_SELECTED:2,
        }
    elif stage == STAGE_FINAL_QUOTE:
        switcher = {
            FINAL_QUOTE_SEND_TO_CLIENT : 1,
            FINAL_QUOTE_SIGNED : 2,
            FINAL_QUOTE_SEND_TO_INSURER : 3
        }
    elif stage == STAGE_PAYMENT:
        switcher = {
            PAYMENT_SEND_TO_CLIENT : 1,
            PAYMENT_CONFIRMATION : 2,
            PAYMENT_SEND_TO_INSURER : 3
        }
    elif stage == STAGE_POLICY_ISSUANCE:
        switcher = {
            POLICY_ISSUANCE : 1,
            POLICY_ISSUANCE_SEND_EMAIL : 2
        }
    elif stage == STAGE_HOUSE_KEEPING:
        return 1
    elif stage == STAGE_WON:
        return 1
    else:
        return 1

    return switcher.get(sub_stage.lower(), 0)


def GetPlanDetails(*args, **kwargs):
    permission_required = 'auth.list_motor_deals'
    
    
    data = dict()
    pk = kwargs.get('pk')
    plans = Plan.objects.all()
    quoted_plan = Plan.objects.filter(pk = pk)
    if quoted_plan.exists():
        quoted_plan = quoted_plan[0]
    area_of_cover = []
    copayments = []
    annual_limits = []
    alternative_medicines = []
    physiotherapy = []
    response = []
    #serialized_qs = serializers.serialize('json', queryset)
    #for plan in plans:
    # for area in plan.area_of_cover.all():
    #     area_of_cover.append(area)

    # for copayment in plan.copayment.all():
    #     copayments.append(copayment)

    # for limit in plan.annual_limit.all():
    #     annual_limits.append(limit)

    # for copayment in plan.alternative_medicine.all():
    #     alternative_medicines.append(copayment)

    # for session in plan.physiotherapy.all():
    #     physiotherapy.append(session)

    #plan_serializer = PlanSerializer(plan)

    response.append({
                    'id': quoted_plan.pk,
                    'product_id': quoted_plan.plan.pk,

                    'plan_logo': quoted_plan.plan.logo.url,
                    'plan_name': quoted_plan.plan.name,

                    
                    'premium': "{:,}".format(quoted_plan.total_premium),
                    'insurer_quote_reference': quoted_plan.insurer_quote_reference,
                    'payment_frequency': quoted_plan.payment_frequency,
                    'area_of_cover': quoted_plan.area_of_cover,
                    'copayment': quoted_plan.copayment,
                    'deductible': quoted_plan.deductible,
                    'network': quoted_plan.network,

                    'annual_limit': quoted_plan.annual_limit,

                    'physiotherapy': quoted_plan.physiotherapy,
                    'alternative_medicine': quoted_plan.alternative_medicine,
                    'maternity_benefits': quoted_plan.maternity_benefits,
                    'maternity_waiting_period': quoted_plan.maternity_waiting_period,
                    'dental_benefits': quoted_plan.dental_benefits,
                    'wellness_benefits': quoted_plan.wellness_benefits,
                    'optical_benefits': quoted_plan.optical_benefits,
                    'is_renewal_plan': quoted_plan.is_renewal_plan,
                    'plan_renewal_document': quoted_plan.plan_renewal_document,                    
                })
    
    return JsonResponse(response, safe=False)

    data = {
        'is_payment_frequency_fixed': plan.is_payment_frequency_fixed,
        'is_area_of_cover_fixed': plan.is_area_of_cover_fixed,
        'is_copayment_fixed': plan.is_copayment_fixed,
        'is_deductible_fixed': plan.is_deductible_fixed,
        'is_network_fixed': plan.is_network_fixed,
        'code': plan.code,
        #'allows_agency_repair': product.allows_agency_repair,
        #'is_tpl_product': product.is_tpl_product,
        'logo': plan.get_logo(),
        'area_of_cover': area_of_cover ,
        'copayments': copayments ,
        #'addons': product.get_add_ons(),
    }
    return JsonResponse(OrderedDict([
        ('data', plan_serializer.data)
        ]))

def GetCountryByName(code):
    if code.lower() == 'other':
        return 'other'
    if code:
        searched_list = list(filter(lambda country: country[0] in code, COUNTRIES))
        return searched_list[0][1]
    else:
        return ''
    

def GetQuotedPlanDetails(quote, **kwargs):
    for_quote_form = kwargs.get('quote_form', None)
    if quote:
        quoted_plans = quote.get_editable_quoted_plans()
        quoted_plans_data = []
        for qp in quoted_plans:
            if for_quote_form == True:
                    plan_data = {
                    "id":qp.id,
                    "plan_name":qp.plan.name,
                    "insurer_name":qp.plan.insurer.name,
                    "insurer_logo":qp.plan.insurer.logo.url,
                    "annual_limit":qp.annual_limit.id,
                    "geographical_cover":qp.area_of_cover.id if qp.area_of_cover else '',
                    "consultation_copay":qp.consultation_copay.id if qp.consultation_copay else '',
                    "diagnostics_copay":qp.diagnostics_copay.id if qp.diagnostics_copay else '',
                    "pharmacy_copay":qp.pharmacy_copay.id if qp.pharmacy_copay else '',
                    "network":qp.network.id if qp.network else '',
                    "pre_existing_cover":qp.plan.pre_existing_cover ,
                    "dental_benefits":qp.dental_benefits.id if qp.dental_benefits else '',
                    "optical_benefits":qp.optical_benefits.id if qp.optical_benefits else '',
                    "maternity_benefits":qp.maternity_benefits.id if qp.maternity_benefits else '',
                    "Maternity_waiting_period":qp.maternity_waiting_period.id if qp.maternity_waiting_period else '',
                    "wellness_benefits":qp.wellness_benefits.id if qp.wellness_benefits else '',
                    "alternative_medicine":qp.alternative_medicine.id if qp.alternative_medicine else '',
                    "physiotherapy":qp.physiotherapy.id if qp.physiotherapy else '',
                    "total_premium":qp.total_premium,
                    "is_renewal":qp.is_renewal_plan,
                    "currency":qp.plan.currency,
                    "is_repatriation_benefit_enabled":qp.is_repatriation_benefit_enabled,
                }
            else:
                plan_data = {
                    "id":qp.id,
                    "coverage_type":qp.plan.coverage_type,
                    "plan_name":qp.plan.name,
                    "insurer_name":qp.plan.insurer.name,
                    "insurer_logo":qp.plan.insurer.logo.url,
                    "annual_limit":qp.annual_limit.limit if qp.annual_limit else '',
                    "inpatient_deductible":qp.inpatient_deductible.deductible if qp.inpatient_deductible else '',
                    "geographical_cover":qp.area_of_cover.area if qp.area_of_cover else '',
                    "consultation_copay":qp.consultation_copay.copayment if qp.consultation_copay else '',
                    "diagnostics_copay":qp.diagnostics_copay.copayment if qp.diagnostics_copay else '',
                    "pharmacy_copay":qp.pharmacy_copay.copayment if qp.pharmacy_copay else '',
                    "network":qp.network.network if qp.network else '',
                    "pre_existing_cover":qp.pre_existing_cover.cover if qp.pre_existing_cover else '',
                    "dental_benefits":qp.dental_benefits.benefit if qp.dental_benefits else '',
                    "optical_benefits":qp.optical_benefits.benefit if qp.optical_benefits else '',
                    "maternity_benefits":qp.maternity_benefits.benefit if qp.maternity_benefits else '',
                    "Maternity_waiting_period":qp.maternity_waiting_period.period if qp.maternity_waiting_period else '',
                    "wellness_benefits":qp.wellness_benefits.benefit if qp.wellness_benefits else '',
                    "alternative_medicine":qp.alternative_medicine.medicine if qp.alternative_medicine else '',
                    "physiotherapy":qp.physiotherapy.sessions if qp.physiotherapy else '',
                    "total_premium": qp.plan.basic_plan_premium if quote.deal.stage == STAGE_BASIC else qp.total_premium,
                    "is_renewal":qp.is_renewal_plan,
                    "plan_renewal_document":qp.plan_renewal_document.url if qp.plan_renewal_document else '',
                    "network_list_inpatient":qp.plan.tpa.network_list_inpatient.url if qp.plan.tpa.network_list_inpatient else qp.plan.network_list_inpatient.url if qp.plan.network_list_inpatient else '',
                    "network_list_outpatient":qp.plan.tpa.network_list_outpatient.url if qp.plan.tpa.network_list_outpatient else qp.plan.network_list_outpatient.url if qp.plan.network_list_outpatient else '',
                    "policy_wording":qp.plan.policy_wording.url if qp.plan.policy_wording else '',
                    "table_of_benefits":qp.plan.table_of_benefits.url if qp.plan.table_of_benefits else '',
                    "maf":qp.plan.maf.url if qp.plan.maf else '',
                    "census":qp.plan.census.url if qp.plan.census else '',
                    "bor":qp.plan.bor.url if qp.plan.bor else '',
                    "currency":qp.currency.name if qp.currency else qp.plan.currency,
                    "is_repatriation_benefit_enabled":qp.is_repatriation_benefit_enabled,
                    "payment_frequency": qp.payment_frequency.frequency,
                }
                if qp.is_repatriation_benefit_enabled and qp.plan.is_repatriation_benefit_enabled:
                    plan_data.update({
                        'repatriation_benefits': qp.plan.repatriation_benefits
                    })
                if qp.plan.coverage_type == "basic":
                    ctx = {
                        
                    }
                    popup_template = qp.plan.popup_template
                    template = Template(popup_template)
                    popup_template_content = template.render(Context(ctx))
                    
                    plan_data.update({
                        'popup_template':popup_template_content,
                        'basic_plan_url': qp.plan.basic_plan_url,
                    })
                
            quoted_plans_data.append(plan_data)

        return quoted_plans_data

def GetAdditionalMemberDetails(primary_member):
    members_data = []
    for member in primary_member.additional_members.all():
        data = {
            "id":member.id,
            "relation" : member.relation,
            "name" : member.name,
            "dob" : member.dob,
            "nationality" : member.nationality,
            "country_of_stay" : member.country_of_stay,
            "country_of_stay" : member.country_of_stay,
            "order" : member.order,
            "premium" : member.premium,
        }
        members_data.append(data)
    
    return members_data

def GetSelectedPlanDetails(qp):
    plan_data = {
                    "id":qp.id,
                    "plan_name":qp.plan.name,
                    "insurer_name":qp.plan.insurer.name,
                    "insurer_logo":qp.plan.insurer.logo.url,
                    "annual_limit":qp.annual_limit.limit,
                    "geographical_cover":qp.area_of_cover.area if qp.area_of_cover else '',
                    "consultation_copay":qp.consultation_copay.copayment if qp.consultation_copay else '',
                    "diagnostics_copay":qp.diagnostics_copay.copayment if qp.diagnostics_copay else '',
                    "pharmacy_copay":qp.pharmacy_copay.copayment if qp.pharmacy_copay else '',
                    "network":qp.network.network if qp.network else '',
                    "pre_existing_cover":qp.pre_existing_cover.cover if qp.pre_existing_cover else '',
                    "dental_benefits":qp.dental_benefits.benefit if qp.dental_benefits else '',
                    "optical_benefits":qp.optical_benefits.benefit if qp.optical_benefits else '',
                    "maternity_benefits":qp.maternity_benefits.benefit if qp.maternity_benefits else '',
                    "Maternity_waiting_period":qp.maternity_waiting_period.period if qp.maternity_waiting_period else '',
                    "wellness_benefits":qp.wellness_benefits.benefit if qp.wellness_benefits else '',
                    "alternative_medicine":qp.alternative_medicine.medicine if qp.alternative_medicine else '',
                    "physiotherapy":qp.physiotherapy.sessions if qp.physiotherapy else '',
                    "total_premium":qp.total_premium,
                    "policy_wording":qp.plan.policy_wording.url if qp.plan.policy_wording else "",
                    "network_list_inpatient":qp.plan.tpa.network_list_inpatient.url if qp.plan.tpa.network_list_inpatient else qp.plan.network_list_inpatient.url if qp.plan.network_list_inpatient else '',
                    "network_list_outpatient":qp.plan.tpa.network_list_outpatient.url if qp.plan.tpa.network_list_outpatient else qp.plan.network_list_outpatient.url if qp.plan.network_list_outpatient else '',
                    "table_of_benefits":qp.plan.table_of_benefits.url if qp.plan.table_of_benefits else "",
                    "maf":qp.plan.maf.url if qp.plan.maf else "",
                    "census":qp.plan.census.url if qp.plan.census else "",
                    "bor":qp.plan.bor.url if qp.plan.bor else "",
                    "payment_frequency": qp.payment_frequency.frequency,
                    "is_renewal": qp.is_renewal_plan,
                    "plan_renewal_document": qp.plan_renewal_document.url if qp.plan_renewal_document else '',
                }

    return plan_data


def EmirateText(text):
    emirate = {
            'DU':'Dubai',
            'AD':'Abu Dhabi',
            'SJ':'Sharjah',
            'AJ':'Ajman',
            'RK':'Ras Al Khaimah',
            'FJ':'Fujairah',
            'UQ':'Umm Al Quwain',
        }
    return emirate.get(text, text)

def GeographicalCoverageText(geographical_coverage):
        coverage = {
            'local':'Local',
            'regional':'Regional',
            'worldwide_except_us':'Worldwide Except US',
            'worldwide':'Worldwide',
        }
        return coverage.get(geographical_coverage, geographical_coverage)

    
def AdditionalBenefitsText(additional_benefit):
        benefit = {
            'health_screen':'Health Screen',
            'dental':'Dental',
            'other':'Other',
        }
        return benefit.get(additional_benefit, additional_benefit)
    

def IndicativeBudgetText(indicative_budget):
        budget = {
            'below1k':'Below 1k',
            'below4k':'Below 4k',
            '2to4k':'2-4k',
            '4to8k':'4-8k',
            'above8k':'Above 8k',
            '8kplus':'Above 8k',
            'notsure':'Not Sure',
        }
        return budget.get(indicative_budget, indicative_budget)

def SalaryBandText(text):
    budget = {
            'above_4k':'Above 4k',
            'below_4k':'Below 4k',            
        }
    return budget.get(text, text)

def get_deal_visa(visa):
    visa = visa.lower()
    visa = visa.replace(' ', '')
    if not visa:
            return 'Non UAE resident'
    elif visa and (visa == 'abudhabi'):
            return 'Abu Dhabi'
    elif visa and (visa == 'dubai'):
            return 'Dubai'
    else:
            return 'Northern Emirates'
            

def get_email_type(stage):
    switcher = {
        STAGE_NEW : 'new_deal',
        STAGE_QUOTE : 'quote',
        STAGE_DOCUMENTS : 'documents',        
        STAGE_FINAL_QUOTE :'final_quote',
        STAGE_PAYMENT : 'payment',
        STAGE_POLICY_ISSUANCE: 'policy_issuance',
        STAGE_HOUSE_KEEPING: 'housekeeping',        
    }

    return switcher.get(stage.lower(), 'new_deal')