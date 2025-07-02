from auto_quoter.uic.rate_book_base import UICRateBookBase


class UICStandardRateBook(UICRateBookBase):
    PRODUCT_NAME = 'Standard'

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
        if deal.get_age_of_car_since_registration() > 10:
            return False, 'This plan is not available for vehicles older than 10 years'

        return super().can_generate_quote(deal, form_data)
