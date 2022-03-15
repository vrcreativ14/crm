from decimal import Decimal, ROUND_HALF_UP
from re import template
from mortgage.constants import VAT_PERCENTAGE 
from mortgage.models import GovernmentFee, Eibor, SegmentedRate, Bank
import numpy_financial as npf
import pandas as pd


class BankHelper:
    
    def __init__(self, bank, property_price, mortgage_amount, tenure, govt_fee_key=GovernmentFee.objects.last().pk, **kwargs):
        self.bank = bank
        self.property_price = property_price
        self.mortgage_amount = mortgage_amount
        self.govt_fee = GovernmentFee.objects.get(pk=govt_fee_key)
        # if not bank.add_fees_to_loan_amount:
        #     self.mortgage_amount = self.mortgage_amount + Decimal(self.govt_fee.trustee_center_fee)

        self.tenure = tenure
        deal = kwargs.get('deal',None)
        self.is_property_reg_financed = deal.is_property_reg_financed if deal else False
        self.is_real_estate_fee_financed = deal.is_real_estate_fee_financed if deal else False
        self.ltv = deal.l_tv if deal else 80

    @property
    def get_down_payment(self):  # calculate the down payment
        down_payment = self.property_price - self.mortgage_amount

        # if  self.bank.add_fees_to_loan_amount:
        #     down_payment = down_payment + Decimal(self.govt_fee.trustee_center_fee)

        return down_payment

    @property
    def get_bank_processing_fee(self):  # calculate bank processing fee
        fee = float(self.mortgage_amount) * self.bank.bank_processing_fee_rate / 100 
        # if self.bank.bank_processing_fee_extra:
        #     fee = fee + self.bank.bank_processing_fee_extra

        # if self.bank.max_bank_processing_fee:
        #     if self.bank.max_bank_processing_fee < fee:
        #         return self.bank.max_bank_processing_fee

        return fee

    @property
    def get_life_insurance_monthly(self):  # calculate the life insurance per month
        return (
            self.mortgage_amount * (self.bank.life_insurance_monthly_rate/100)
        )
        
    @property
    def get_property_insurance_yearly(self):
        return (
            self.property_price * self.bank.property_insurance_yearly_rate / 100
        )

    # GOVERNMENT FEES
    @property
    def trustee_center_fee_vat(self):
        return self.govt_fee.trustee_center_fee

    @property
    def land_dep_property_registration(self):
        return self.property_price * self.govt_fee.property_fee_rate/100 + self.govt_fee.property_fee_addition

    @property
    def land_dep_mortgage_registration(self):
        return self.mortgage_amount * self.govt_fee.mortgage_fee_rate/100 + self.govt_fee.mortgage_fee_addition

    @property
    def real_estate_fee_vat(self):
        real_state_fee = self.property_price * (self.govt_fee.real_state_fee/100)
        #real_state_fee = real_state_fee + real_state_fee * VAT_PERCENTAGE
        return real_state_fee

    # FINALS
    @property
    def calculate_total_down_payment(self):
        # total_down_payment =  self.get_down_payment + self.bank.property_valuation_fee 
        # total_down_payment += self.get_bank_processing_fee + self.get_life_insurance_monthly 
        # total_down_payment += self.get_property_insurance_yearly + self.trustee_center_fee_vat 
        # total_down_payment += self.land_dep_mortgage_registration
        # if self.bank.extra_financing_allowed == True:
        #     if self.is_real_estate_fee_financed == False:
        #         total_down_payment += self.real_estate_fee_vat
        #     else:
        #         total_down_payment -= self.real_estate_fee_vat
        #     if self.is_real_estate_fee_financed == False:
        #         total_down_payment += self.land_dep_property_registration
        #     else:
        #         total_down_payment -= self.land_dep_property_registration
        # else:
        #     total_down_payment += self.land_dep_property_registration + self.real_estate_fee_vat
            
        # return total_down_payment
        return (
            self.get_down_payment
            + self.bank.property_valuation_fee
            + self.get_bank_processing_fee
            + self.get_life_insurance_monthly
            + self.get_property_insurance_yearly
            + self.trustee_center_fee_vat
            + self.land_dep_mortgage_registration
            + self.land_dep_property_registration
            + self.real_estate_fee_vat
        )

    @property
    def calculate_extra_financing(self):
        extra_financing = 0
        if self.is_property_reg_financed == True:
            extra_financing += self.land_dep_property_registration
        if self.is_real_estate_fee_financed == True:
            extra_financing += self.real_estate_fee_vat
        
        return extra_financing - 580
        # return (
        #     self.land_dep_property_registration + self.real_estate_fee_vat - 580
        # )

    @property
    def get_extra_financing(self):
        #return self.calculate_extra_financing * 80 / 100
        return self.calculate_extra_financing * (self.ltv / 100)

    @property
    def calculate_net_down_payment(self):
        if self.bank.extra_financing_allowed == True:
            return self.calculate_total_down_payment - self.get_extra_financing
        else:
            return self.calculate_total_down_payment

    @property
    def get_updated_mortgage_amount(self):
        if self.bank.extra_financing_allowed:
            extra_financing = 0
            if self.is_property_reg_financed == True:
                extra_financing += self.land_dep_property_registration
            if self.is_real_estate_fee_financed == True:
                extra_financing += self.real_estate_fee_vat

            updated_mortgage = self.mortgage_amount + extra_financing
            return updated_mortgage
        else:
            return self.mortgage_amount
    # calculate the monthly repayment
    @property
    def loan(self):
        return (
            self.property_price - self.calculate_net_down_payment
        )

    @property
    def monthly_repayment(self):
        int_rate = self.bank.interest_rate
        if not self.bank.post_introduction_rate:
            int_rate = int_rate + self.bank.eibor_rate
        repayment = abs(npf.pmt((int_rate/100)/(12), (1)*(self.tenure), self.get_updated_mortgage_amount))
        if pd.isna(repayment):
            repayment = 0
        return repayment

    def test_value(self):
        return self.bank.interest_rate

    @property
    def monthly_repayment_after(self):
        int_rate = self.bank.interest_rate
        if self.bank.post_introduction_rate:
            int_rate = self.bank.post_introduction_rate + self.bank.eibor_rate
        else:
            int_rate = int_rate + self.bank.eibor_rate
        repayment = abs(npf.pmt((int_rate/100)/(12), (1)*(self.tenure), self.get_updated_mortgage_amount))
        if pd.isna(repayment):
            repayment = 0
        return repayment

    @property
    def monthly_repayment_extra_financing(self):
        int_rate = self.bank.interest_rate
        if not self.bank.post_introduction_rate:
            int_rate = int_rate + self.bank.eibor_rate  
        repayment = abs(npf.pmt((int_rate/100)/(12), (1)*(self.tenure), self.get_extra_financing))
        if pd.isna(repayment):
            repayment = 0
        return repayment


def get_quote_data(quote, order=None):

    banks = quote.bank.all()
    if order:
        banks = [order.bank]
    deal = quote.deals
    banks_list = []

    if quote.is_segmented:
        for bank in banks:
            segmented_rate = SegmentedRate.objects.filter(quote=quote, bank=bank)
            if segmented_rate:
                rate = segmented_rate.last().rate
                setattr(bank, "interest_rate", rate.interest_rate)
                setattr(bank, "eibor_rate", rate.eibor_rate)
                setattr(bank, "eibor_duration", rate.eibor_duration)
                setattr(
                    bank,
                    "introduction_period_in_years",
                    rate.introduction_period_in_years,
                )
                setattr(bank, "post_introduction_rate", rate.post_introduction_rate)
                setattr(bank, "eibor_post_duration", rate.eibor_post_duration)
                banks_list.append(bank)
            else:
                bank = Bank.objects.bank_info(pk=bank.pk)
                banks_list.append(bank)
    else:
        banks_list = []
        for bank in banks:
            bank = Bank.objects.bank_info(pk=bank.pk)
            banks_list.append(bank)
    final_data = []

    for bank in banks_list:
        data = BankHelper(bank, deal.property_price, deal.loan_amount, deal.tenure, deal.govt_fee.pk, deal = deal)
        total_monthly_repayment_with_extra_financing = int(data.monthly_repayment_after) + int(data.monthly_repayment_extra_financing)
        mortgage_emi = int(data.monthly_repayment) + int(data.monthly_repayment_extra_financing)
        bank_data = {
            "bank_pk": bank.pk,
            "bank_name": bank.name,
            "bank_logo": bank.logo.url if bank.logo else None,
            "eibor_duration": bank.eibor_duration,
            "eibor_post_duration": bank.eibor_post_duration,
            "down_payment": int(data.get_down_payment),
            "bank_processing_fee": int(data.get_bank_processing_fee),
            "life_insurance_monthly": int(data.get_life_insurance_monthly),
            "property_insurance_yearly": int(data.get_property_insurance_yearly),
            "trustee_center_fee_vat": int(data.trustee_center_fee_vat),
            "land_dep_property_registration": int(data.land_dep_property_registration),
            "land_dep_mortgage_registration": int(data.land_dep_mortgage_registration),
            "real_estate_fee_vat": int(data.real_estate_fee_vat),
            "total_down_payment": int(data.calculate_total_down_payment),
            "extra_financing": int(data.get_extra_financing),
            "net_down_payment": int(data.calculate_net_down_payment),
            "loan": int(data.loan),
            "monthly_repayment": int(data.monthly_repayment),
            "updated_mortgage_amount":int(data.get_updated_mortgage_amount),
            "full_settlement_percentage": bank.full_settlement_percentage,
            "full_settlement_max_value": bank.full_settlement_max_value,
            "free_partial_payment_per_year": bank.free_partial_payment_per_year,
            "interest_rate": bank.interest_rate,
            "introduction_period_in_years": bank.introduction_period_in_years,
            "post_introduction_rate": bank.post_introduction_rate,
            "poverty_valuation_fee": bank.property_valuation_fee,
            "bank_extra_financing_allowed": bank.extra_financing_allowed,
            "bank_type": bank.type,
            f"monthly_repayment_after__years_main_amount": int(data.monthly_repayment),
            f"monthly_repayment_after__years_after_the_fix_period": int(data.monthly_repayment_after),
            f"monthly_repayment_extra_financing": int(data.monthly_repayment_extra_financing),
            f"total_monthly_repayment_with_extra_financing": total_monthly_repayment_with_extra_financing,
            f"mortgage_emi" : mortgage_emi,
            f"sample_form": bank.sample_form.url,
        }
        final_data.append(bank_data)

    return final_data

def deal_stages_to_number(argument):
    switcher = {
        'new': 0,
        'new deal': 0,
        'quote sent': 1,
        'quote': 1,
        'preapproval': 2,
        'valuation': 3,
        'offer': 4,
        'settlement': 5,
        'loandisbursal': 6,
        'propertytransfer': 7,
        'won': 8,
        'lost': 9,        
    }

    return switcher.get(argument.lower(), 0)