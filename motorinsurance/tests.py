from django.test import TestCase

from motorinsurance_shared.models import Product


class MotorInsuranceProductTestCase(TestCase):
    def test_validate_product_attribute(self):
        valid_boolean = {
            'available': True,
            'add_on': False,

            'description': 'Description is always required.',
            'help_text': 'Help text is optional.'
        }
        self.assertTrue(Product.validate_product_attribute(valid_boolean)[0],
                        'Boolean attribute value is valid')

        invalid_boolean = {
            'available': True,
            'add_on': False,

            'help_text': 'Help text is optional.'
        }
        self.assertFalse(Product.validate_product_attribute(invalid_boolean)[0],
                         'Boolean attribute value is invalid without a description')

        valid_add_on = {
            'available': True,
            'add_on': True,

            'description': 'Description is always required.',
            'price': 200
        }
        self.assertTrue(Product.validate_product_attribute(valid_add_on)[0],
                        'Add On attribute value is valid')

        invalid_add_on = {
            'available': True,
            'add_on': True,

            'description': 'Description is always required.',
        }
        self.assertFalse(Product.validate_product_attribute(invalid_add_on)[0],
                         'Add On attribute is invalid without a price value')

        self.assertFalse(Product.validate_product_attribute({})[0],
                         'Empty dict is an invalid attribute value.')
        self.assertFalse(Product.validate_product_attribute({'key': 'value'})[0],
                         'Random dict is an invalid attribute value.')
