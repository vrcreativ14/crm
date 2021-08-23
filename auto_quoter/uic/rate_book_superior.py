from auto_quoter.uic.rate_book_base import UICRateBookBase


class UICSuperiorRateBook(UICRateBookBase):
    PRODUCT_NAME = 'Superior'

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

    AGENCY_REPAIR_LOADING_TABLE = {
        '0 - 70K': {
            1: 0.0,
            2: 35.0
        },

        '70K - 150K': {
            1: 0.0,
            2: 0.0,
            3: 25.0,
            4: 40.0,
            5: 60.0
        },

        '150K - 500K': {
            1: 0.0,
            2: 0.0,
            3: 10.0,
            4: 30.0,
            5: 55.0
        }
    }

    def can_generate_quote(self, deal, form_data):
        if deal.get_age_of_car_since_registration() > 12:
            return False, 'This plan is not available for vehicles older than 12 years'

        return super().can_generate_quote(deal, form_data)