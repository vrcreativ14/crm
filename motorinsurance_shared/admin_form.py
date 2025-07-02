from django import forms

from motorinsurance_shared.models import Product


class ProductAttributeMultiWidget(forms.MultiWidget):
    template_name = 'motorinsurance_shared/admin/product-attribute-multi-widget.djhtml'

    def __init__(self, **kwargs):
        widgets = (
            forms.CheckboxInput(),
            forms.CheckboxInput(),
            forms.TextInput(),
            forms.NumberInput(),
            forms.Textarea()
        )
        super(ProductAttributeMultiWidget, self).__init__(widgets=widgets, **kwargs)

    def decompress(self, value):
        if value is None:
            return [None for key in ['available', 'add_on', 'description', 'price', 'help_text']]

        return [value.get(key, '') for key in ['available', 'add_on', 'description', 'price', 'help_text']]


class ProductAttributeMultiField(forms.MultiValueField):
    widget = ProductAttributeMultiWidget

    def __init__(self, **kwargs):
        fields = (
            forms.BooleanField(required=False, label='Available?'),  # available
            forms.BooleanField(required=False, label='Is add on?'),  # add on
            forms.CharField(max_length=500, label='Description', required=False),  # description
            forms.FloatField(label='Price', required=False),  # price
            forms.CharField(max_length=1000, required=False, label='Help text')  # help text
        )
        super(ProductAttributeMultiField, self).__init__(fields=fields, require_all_fields=False, **kwargs)

    def compress(self, data_list):
        return dict(zip(['available', 'add_on', 'description', 'price', 'help_text'], data_list))


class ProductAdminModelForm(forms.ModelForm):
    rent_a_car = ProductAttributeMultiField()
    road_side_assistance = ProductAttributeMultiField()
    pab_driver = ProductAttributeMultiField()
    pab_passenger = ProductAttributeMultiField()
    pab_family_and_friends = ProductAttributeMultiField()
    fire_and_theft_cover = ProductAttributeMultiField()
    natural_disaster = ProductAttributeMultiField()
    riot_and_strike = ProductAttributeMultiField()
    windscreen_and_glass_damage = ProductAttributeMultiField()
    emergency_medical_expenses = ProductAttributeMultiField()
    personal_belongings = ProductAttributeMultiField()
    replacement_keys_and_locks = ProductAttributeMultiField()
    oman_cover = ProductAttributeMultiField()
    off_road_cover = ProductAttributeMultiField()
    ambulance_cover = ProductAttributeMultiField()
    third_party_property_damage = ProductAttributeMultiField()
    third_party_bodily_injury = ProductAttributeMultiField()

    class Meta:
        model = Product
        fields = '__all__'
