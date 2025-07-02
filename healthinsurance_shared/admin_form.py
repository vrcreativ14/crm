from django import forms

from healthinsurance_shared.models import Plan, Insurer


class ProductAttributeMultiWidget(forms.MultiWidget):
    template_name = 'healthinsurance_shared/admin/product-attribute-multi-widget.djhtml'

    def __init__(self, **kwargs):
        widgets = (
            forms.CheckboxInput(),
            forms.CheckboxInput(),
            forms.CheckboxInput(),
            forms.TextInput(),
            forms.TextInput(),
            forms.TextInput(),            
            forms.TextInput(),            
            forms.Textarea()
        )
        super(ProductAttributeMultiWidget, self).__init__(widgets=widgets, **kwargs)

    def decompress(self, value):
        print(self)
        print(value)
        if value is None:
            return [None for key in ['is_benefit_only_for_home_country', 'is_accomodation_cost_covered', 'do_repatriation_when_screened_blood_inavailable', 'accomodation_cost_cover','accompanying_person_expense', 'family_members_travel_expense', 'members_with_critical_patient_travel_expense','help_text']]

        return [value.get(key, '') for key in ['is_benefit_only_for_home_country', 'is_accomodation_cost_covered', 'do_repatriation_when_screened_blood_inavailable', 'accomodation_cost_cover', 'accompanying_person_expense', 'family_members_travel_expense','members_with_critical_patient_travel_expense','help_text']]


class ProductAttributeMultiField(forms.MultiValueField):
    widget = ProductAttributeMultiWidget

    def __init__(self, **kwargs):
        fields = (
            forms.BooleanField(label='Benefit only applies when your home country is within your area of cover?', required=False),  
            forms.BooleanField(label='Accomodation costs covered?', required=False),  
            forms.BooleanField(label='Repatriation in the event of unavailabilty of adequately screened blood?', required=False),             
            forms.CharField(max_length=200, label="Hotel accomodation costs cover", required=False),  
            forms.CharField(max_length=200, label="Expenses for one person accompanying a repatriated person", required=False),  
            forms.CharField(max_length=200, label="Travel costs of insured family menbers in the event of a repatriation", required=False),  
            forms.CharField(max_length=200, label="Travel costs of insured members to be with a family member who is at peril of death or died", required=False), 
            forms.CharField(max_length=1000, label='Help text', required=False),  
        )
        super(ProductAttributeMultiField, self).__init__(fields=fields, require_all_fields=False, **kwargs)

    def compress(self, data_list):
        return dict(zip(['is_benefit_only_for_home_country',
         'is_accomodation_cost_covered', 
         'do_repatriation_when_screened_blood_inavailable',
         'accomodation_cost_cover',
         'accompanying_person_expense', 
         'family_members_travel_expense', 
         'members_with_critical_patient_travel_expense',
         'help_text'], data_list))


class ProductAdminModelForm(forms.ModelForm):
    repatriation_benefits = ProductAttributeMultiField()
    class Meta:
        model = Plan
        fields = '__all__'

class InsurerAdminForm(forms.ModelForm):
    replace_existing_documents_in_plans = forms.BooleanField(required=False)
    
    def save(self, *args, **kwargs):
        replace_existing_documents =  self.cleaned_data.get('replace_existing_documents_in_plans', None)        
        if replace_existing_documents == True:
            maf =  self.cleaned_data.get('maf', None)
            census =  self.cleaned_data.get('census', None)
            bor =  self.cleaned_data.get('bor', None)
            if maf or census or bor:
                insurer_plans = Plan.objects.filter(insurer = self.instance)
                for plan in insurer_plans:
                    if maf:
                        plan.maf = maf
                    if census:
                        plan.census = census
                    if bor:
                        plan.bor = bor
                    plan.save(from_insurer_admin = True)
        return super(InsurerAdminForm, self).save(commit=False)
    class Meta:
        model = Insurer
        fields = '__all__'
