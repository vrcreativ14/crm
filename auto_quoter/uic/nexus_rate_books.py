from auto_quoter.uic.rate_book_standard import UICStandardRateBook
from auto_quoter.uic.rate_book_superior import UICSuperiorRateBook
from motorinsurance.constants import INSURER_UI, INSURANCE_TYPE_COMPREHENSIVE
from motorinsurance.helpers import is_ncd_more_than


class NexusRateBookFeatures:
    def get_deductible(self, deal, form_data):
        insured_value = form_data['insured_value']

        if deal.current_insurer == INSURER_UI and deal.claim_certificate_available:
            if insured_value <= 50000:
                return 200
            elif insured_value <= 100000:
                return 350
            elif insured_value <= 250000:
                return 500
            elif insured_value <= 500000:
                return 750
        else:
            if insured_value <= 50000:
                return 350
            elif insured_value <= 100000:
                return 500
            elif insured_value <= 250000:
                return 750
            elif insured_value <= 500000:
                return 1000

    def can_quote_agency(self, deal, form_data):
        if not deal.is_new_car() and not deal.current_insurance_type == INSURANCE_TYPE_COMPREHENSIVE:
            return False, 'This plan is not available for vehicles whose current cover is not comprehensive insurance.'

        car_age = deal.get_age_of_car_since_registration()
        insured_value = form_data['insured_value']

        if insured_value <= 70000 and car_age > 2:
            return False, 'This plan is not available for vehicles older than 3 years and valued below Dhs 70K'
        elif car_age > 5:
            return False, 'This plan is not available for vehicles older than 5 years'

        if car_age > 2 and not form_data['previous_repair_condition_is_agency']:
            return False, 'Agency repair only available when previous year repair condition is agency repair'

        if car_age == 2 and not is_ncd_more_than(deal.years_without_claim, 1):
            return False, 'This plan requires a 1 year no claim letter'
        elif car_age == 3 and not (is_ncd_more_than(deal.years_without_claim, 1) and deal.claim_certificate_available):
            return False, 'This plan requires a 1 year no claim letter'
        elif car_age == 4 and not (is_ncd_more_than(deal.years_without_claim, 2) and deal.claim_certificate_available):
            return False, 'This plan requires a 2 year no claim letter'
        elif car_age == 5 and not (is_ncd_more_than(deal.years_without_claim, 2) and deal.claim_certificate_available):
            return False, 'This plan requires a 2 year no claim letter'

        return True, ''

    def generate_name_for_product_we_cant_quote(self, deal, form, postfix=''):
        if form['insured_value'] <= 70000:
            return 'Union Insurance {} - VV < 70,000{}'.format(self.PRODUCT_NAME, postfix)
        else:
            return 'Union Insurance {} - VV > 70,001{}'.format(self.PRODUCT_NAME, postfix)


class NexusSilverRateBook(NexusRateBookFeatures, UICStandardRateBook):
    PRODUCT_NAME = 'Silver'

    RATES_TABLE = {
        '0 - 70K': {
            'garage': {
                'saloon': {
                    'rate': 2.61,
                    'min': 1300
                },
                'station_wagon': {
                    'rate': 2.61,
                    'min': 2000
                },
                'sports': {
                    'rate': 3.52,
                    'min': 2500
                }
            },

            'agency': {
                'saloon': {
                    'rate': 3.80,
                    'min': 1500
                },
                'station_wagon': {
                    'rate': 3.80,
                    'min': 2000
                },
                'sports': {
                    'rate': 4.28,
                    'min': 2500
                }
            }

        },

        '70K - 150K': {
            'garage': {
                'saloon': {
                    'rate': 2.31,
                    'min': 1300
                },
                'station_wagon': {
                    'rate': 2.25,
                    'min': 2000
                },
                'sports': {
                    'rate': 3.04,
                    'min': 2500
                }
            },

            'agency': {
                'saloon': {
                    'rate': 3.23,
                    'min': 1300
                },
                'station_wagon': {
                    'rate': 3.23,
                    'min': 2000
                },
                'sports': {
                    'rate': 4.04,
                    'min': 2500
                }
            }
        },

        '150K - 500K': {
            'garage': {
                'saloon': {
                    'rate': 1.96,
                    'min': 1300
                },
                'station_wagon': {
                    'rate': 1.96,
                    'min': 2000
                },
                'sports': {
                    'rate': 2.31,
                    'min': 2500
                }
            },

            'agency': {
                'saloon': {
                    'rate': 2.61,
                    'min': 1300
                },
                'station_wagon': {
                    'rate': 2.61,
                    'min': 2000
                },
                'sports': {
                    'rate': 3.15,
                    'min': 2500
                }
            }
        }
    }


class NexusGoldRateBook(NexusRateBookFeatures, UICSuperiorRateBook):
    PRODUCT_NAME = 'Gold'

    RATES_TABLE = {
        '0 - 70K': {
            'garage': {
                'saloon': {
                    'rate': 2.77,
                    'min': 1400
                },
                'station_wagon': {
                    'rate': 2.77,
                    'min': 2000
                },
                'sports': {
                    'rate': 3.73,
                    'min': 2500
                }
            },

            'agency': {
                'saloon': {
                    'rate': 4.0,
                    'min': 1600
                },
                'station_wagon': {
                    'rate': 4.0,
                    'min': 2000
                },
                'sports': {
                    'rate': 4.50,
                    'min': 2500
                }
            }
        },

        '70K - 150K': {
            'garage': {
                'saloon': {
                    'rate': 2.43,
                    'min': 1400
                },
                'station_wagon': {
                    'rate': 2.34,
                    'min': 2000
                },
                'sports': {
                    'rate': 3.24,
                    'min': 2500
                }
            },

            'agency': {
                'saloon': {
                    'rate': 3.33,
                    'min': 1400
                },
                'station_wagon': {
                    'rate': 3.33,
                    'min': 2000
                },
                'sports': {
                    'rate': 4.27,
                    'min': 2500
                }
            }
        },

        '150K - 500K': {
            'garage': {
                'saloon': {
                    'rate': 2.05,
                    'min': 1400
                },
                'station_wagon': {
                    'rate': 2.05,
                    'min': 2000
                },
                'sports': {
                    'rate': 2.42,
                    'min': 2500
                }
            },

            'agency': {
                'saloon': {
                    'rate': 2.70,
                    'min': 1600
                },
                'station_wagon': {
                    'rate': 2.70,
                    'min': 2000
                },
                'sports': {
                    'rate': 3.29,
                    'min': 2500
                }
            }
        }
    }
