from decimal import Decimal

from motorinsurance.models import Quote
from motorinsurance.models import QuotedProduct
from motorinsurance_shared.models import Product


class QuoteResource:
    @classmethod
    def generate_frontend_data_from_quote(cls, quote: Quote):
        quoted_products = list()

        for quoted_product in quote.get_active_quoted_products().order_by("-premium"):
            product = quoted_product.product

            premium = float(quoted_product.premium)
            total_price = float(quoted_product.get_sale_price())

            product_dict = {  # Product dict
                "qp_id": quoted_product.id,
                "name": product.get_display_name(),
                "price": total_price,
                "premium": premium,
                "premium_display": "{:,.0f}".format(premium),
                "total_price": total_price,
                "total_price_display": "{:,.2f}".format(total_price),
                "default_addons": quoted_product.default_add_ons,
                "logo": product.get_logo(),
                "agency_repair": quoted_product.agency_repair,
                "insured_car_value": "{:,}".format(quoted_product.insured_car_value),
                "ncd_required": quoted_product.ncd_required,
                "document_url": product.document_url,
                "tier_1_attributes": cls.get_tier_1_attributes(quote, quoted_product),
                "tier_2_attributes": cls.get_tier_2_attributes(quote, quoted_product)
            }

            quoted_products.append(product_dict)

        return quoted_products

    @classmethod
    def get_tier_1_attributes(cls, quote: Quote, quoted_product: QuotedProduct):
        product = quoted_product.product

        if product.is_tpl_product:
            product_coverage = 'Third Party Liability Coverage only'
            product_coverage_tooltip = 'This coverage is for damage caused to third parties. This policy will not cover you or any damages that may occur to your own car.'
        else:
            product_coverage = 'Comprehensive with {} repairs'.format(
                'agency' if product.allows_agency_repair and quoted_product.agency_repair else 'non-agency'
            )

            if product.repair_type_description_non_agency and not quoted_product.agency_repair:
                product_coverage = product.repair_type_description_non_agency

            product_coverage_tooltip = "With agency repair your insurer will have your car repaired at the authorised workshop and your car's warranty will not be voided. We recommend agency repair for young cars that are still under warranty."

        return [
            cls.create_attribute_dict(
                "Dhs {} excess {}".format(quoted_product.deductible, quoted_product.deductible_extras),
                "If you have an accident and you are judged to be at fault then this is the amount you have to pay "
                "before your insurance benefits start kicking in."
            ),

            cls.create_attribute_dict(product_coverage, product_coverage_tooltip),

            cls.get_rent_a_car_attribute(product),
            cls.get_road_side_assistance_attribute(product),
            cls.get_pab_driver_cover_attribute(product),
            cls.get_pab_family_and_friend_cover_attribute(product)
        ]

    @classmethod
    def get_tier_2_attributes(cls, quote: Quote, quoted_product: QuotedProduct):
        product = quoted_product.product

        return [
            cls.get_pab_passenger_cover_attribute(quote, product),
            cls.get_fire_and_theft_cover_attribute(product),
            cls.get_natural_disaster_cover_attribute(product),
            cls.get_riot_and_strike_cover_attribute(product),
            cls.get_windscreen_and_glass_damage_cover_attribute(product),
            cls.get_emergency_medical_cover_attribute(product),
            cls.get_personal_belongings_cover_attribute(product),
            cls.get_replacement_keys_and_locks_cover_attribute(product),

            cls.get_oman_cover_attribute(product),
            cls.get_off_road_cover_attribute(product),

            cls.get_ambulance_cover_attribute(product),

            cls.get_third_party_property_damage_cover_attribute(product),
            cls.get_third_party_bodily_injury_cover_attribute(product)
        ]

    @classmethod
    def get_rent_a_car_attribute(cls, product):
        if product.rent_a_car['add_on']:
            return cls.create_addon_attribute_dict(
                product.rent_a_car['description'],
                'rent_a_car', product.rent_a_car['price'],
                product.rent_a_car['help_text']
            )
        else:
            return cls.create_attribute_dict(product.rent_a_car['description'], product.rent_a_car['help_text'])

    @classmethod
    def get_road_side_assistance_attribute(cls, product):
        if product.road_side_assistance['add_on']:
            return cls.create_addon_attribute_dict(
                product.road_side_assistance['description'],
                'road_side_assistance', product.road_side_assistance['price'],
                product.road_side_assistance['help_text']
            )
        else:
            return cls.create_attribute_dict(product.road_side_assistance['description'],
                                             product.road_side_assistance['help_text'])

    @classmethod
    def get_oman_cover_attribute(cls, product):
        if product.oman_cover['add_on']:
            return cls.create_addon_attribute_dict(
                product.oman_cover['description'],
                'oman_cover', product.oman_cover['price'],
                product.oman_cover['help_text']
            )
        else:
            return cls.create_attribute_dict(product.oman_cover['description'], product.oman_cover['help_text'])

    @classmethod
    def get_off_road_cover_attribute(cls, product):
        if product.off_road_cover['add_on']:
            return cls.create_addon_attribute_dict(
                product.off_road_cover['description'],
                'off_road_cover', product.off_road_cover['price'],
                product.off_road_cover['help_text']
            )
        else:
            return cls.create_attribute_dict(product.off_road_cover['description'], product.off_road_cover['help_text'])

    @classmethod
    def get_fire_and_theft_cover_attribute(cls, product):
        return cls.create_attribute_dict(product.fire_and_theft_cover['description'],
                                         product.fire_and_theft_cover['help_text'])

    @classmethod
    def get_natural_disaster_cover_attribute(cls, product):
        return cls.create_attribute_dict(product.natural_disaster['description'], product.natural_disaster['help_text'])

    @classmethod
    def get_riot_and_strike_cover_attribute(cls, product):
        return cls.create_attribute_dict(
            product.riot_and_strike['description'],
            product.riot_and_strike['help_text']
        )

    @classmethod
    def get_windscreen_and_glass_damage_cover_attribute(cls, product):
        return cls.create_attribute_dict(product.windscreen_and_glass_damage['description'],
                                         product.windscreen_and_glass_damage['help_text'])

    @classmethod
    def get_emergency_medical_cover_attribute(cls, product):
        return cls.create_attribute_dict(
            product.emergency_medical_expenses['description'],
            product.emergency_medical_expenses['help_text']
        )

    @classmethod
    def get_personal_belongings_cover_attribute(cls, product):
        return cls.create_attribute_dict(
            product.personal_belongings['description'],
            product.personal_belongings['help_text']
        )

    @classmethod
    def get_replacement_keys_and_locks_cover_attribute(cls, product):
        return cls.create_attribute_dict(
            product.replacement_keys_and_locks['description'],
            product.replacement_keys_and_locks['help_text']
        )

    @classmethod
    def get_pab_driver_cover_attribute(cls, product):
        if product.pab_driver['add_on']:
            return cls.create_addon_attribute_dict(
                product.pab_driver['description'],
                'pab_driver', product.pab_driver['price'],
                product.pab_driver['help_text']
            )
        else:
            return cls.create_attribute_dict(product.pab_driver['description'], product.pab_driver['help_text'])

    @classmethod
    def get_pab_passenger_cover_attribute(cls, quote: Quote, product):
        if product.pab_passenger['add_on']:
            addon_price = product.pab_passenger['price'] * quote.deal.number_of_passengers

            return cls.create_addon_attribute_dict(
                product.pab_passenger['description'],
                'pab_passenger', addon_price,
                product.pab_passenger['help_text']
            )
        else:
            return cls.create_attribute_dict(product.pab_passenger['description'], product.pab_passenger['help_text'])

    @classmethod
    def get_pab_family_and_friend_cover_attribute(cls, product):
        return cls.create_attribute_dict(
            product.pab_family_and_friends['description'],
            product.pab_family_and_friends['help_text']
        )

    @classmethod
    def get_ambulance_cover_attribute(cls, product):
        return cls.create_attribute_dict(
            product.ambulance_cover['description'],
            product.ambulance_cover['help_text']
        )

    @classmethod
    def get_third_party_property_damage_cover_attribute(cls, product):
        return cls.create_attribute_dict(product.third_party_property_damage['description'],
                                         product.third_party_property_damage['help_text'])

    @classmethod
    def get_third_party_bodily_injury_cover_attribute(cls, product):
        return cls.create_attribute_dict(product.third_party_bodily_injury['description'],
                                         product.third_party_bodily_injury['help_text'])

    @classmethod
    def create_attribute_dict(cls, label, tooltip=""):
        return {
            "type": "attribute",
            "label": label,
            "tooltip": tooltip
        }

    @classmethod
    def create_addon_attribute_dict(cls, label, code, price, tooltip=""):
        return {
            "type": "addon",
            "label": label,
            "code": code,
            "value": price,
            "tooltip": tooltip,
            "selected": False
        }

    @classmethod
    def get_price_for_add_on(cls, quote: Quote, product: Product, add_on: str):
        if add_on == 'pab_passenger':
            num_passengers_in_car = quote.deal.number_of_passengers
            price = product.pab_passenger['price'] * num_passengers_in_car
        else:
            price = getattr(product, add_on)['price']

        return Decimal(price)

    @classmethod
    def get_price_for_product_with_premium_and_add_ons(cls, quote: Quote, product: Product,
                                                       premium: Decimal, add_ons: [str]):
        total_price = Decimal(premium)
        for add_on in add_ons:
            total_price += cls.get_price_for_add_on(quote, product, add_on)

        return total_price.quantize(Decimal('0.01'))

    @classmethod
    def get_price_for_quoted_product_with_add_ons(cls, quote: Quote, qp: QuotedProduct, add_ons: [str]):
        return cls.get_price_for_product_with_premium_and_add_ons(quote, qp.product, qp.get_sale_price(), add_ons)
