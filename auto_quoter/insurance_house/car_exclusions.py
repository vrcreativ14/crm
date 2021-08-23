"""Data and methods that are used to check if a car is an excluded or referral required model
for UIC."""
import re

# When checking the exclusion and blacklists, we try a full match with the make name. For the models:
# - If the list is empty, all models from the make are included in the list
# - Otherwise each item in the list is used as a regex to match against the model name. Any match means the given model
#   is excluded

exclusion_list = {
    'alfa romeo': [],
    'aston martin': [],
    'audi': [],
    'bmw': [],
    'bentley': [],
    'bugatti': [],
    'cadillac': [],

    'chevrolet': [r'caprice ss', r'lumina ss', r'corvette', r'camaro', r'ssr', r'coupe'],
    'chrysler': [r'fiber gts', r'new yorker', r'300c .* srt', r'300 m', r'cross fire', r'pt cruiser', r'coupe'],

    'citroën': [],

    'dodge': [r'Charger', r'Challenger', r'Fiber', r'Coupe'],

    'ferrari': [],
    'fiat': [],
    'fisker': [],

    'ford': [r'mustang', r'thunderbird', r'^gt', r'cougar mark 7', r'raptor', r'coupe'],
    'honda': [r'prelude', r'legend', r'integra', r'vigor', r's2000', r'nsx', r'crx', r'coupe'],
    'hyundai': [r'coupe', r'veloster'],

    'hummer': [],

    'infiniti': [r'coupe'],

    'jaguar': [r'coupe', r'xk', r'xr'],
    'jeep': [r'Wrangler', r'Grand Cherokee .* SRT'],

    'lamborghini': [],

    'lincoln': [r'town'],

    'lotus': [],

    'lexus': [r'^IS', r'SC', r'coupe'],

    'maserati': [],

    'mazda': [r'coupe', r'sport', r'VX', r'RX7', r'RX5', r'MX3', r'MX5', r'MX6', r'MX7', r'MX8'],
    'mercedes-benz': [r'coupe', r'^(C|S)LK', r'^SL(S|R)', r'^CL', r'E55\b', r'E60\b', r'E63\b', r'E65\b',
                      r'G55\b', r'G63\b', r'G65\b', r'G500\b', r'SL (5|6)00', r'S55\b', r'S63\b', r'S65\b', r'C63\b',
                      r'A250\b', r'A45\b', ],

    'mini': [],

    'mitsubishi': [r'Eclipse', r'coupe', r'Evolution', 'Sigma', 'Magna', 'GT300'],
    'nissan': [r'Titan', r'ZX', r'GT-R', r'\d+Z', r'Maxima', r'Skyline', r'GT', 'coupe'],

    'opel': [],

    'peugeot': [r'CC', r'coupe', r'Sport'],

    'porsche': [],

    'renault': [r'cleo', r'megane', r'spider'],

    'rolls-royce': [],
    'saab': [],
    'škoda': [],
    'seat': [],

    'suzuki': [r'Swift', r'coupe'],
    'subaru': [r'coupe', r'WRX', r'GT', r'STI'],
    'toyota': [r'Supra', r'Cilica', r'Salora', r'Tundra', r'Mark 2', r'coupe', r'FJ'],

    'volkswagen': [],

    'volvo': [r'C(3|4|7|9)0', r'S60', r'Coupe'],
}


def is_car_in_list(deal, list_to_check):
    make = deal.car_make.name
    model_name = deal.get_car_trim()

    if make.lower() in list_to_check:
        included_models_config = list_to_check[make.lower()]
        invert_check = False

        if isinstance(included_models_config, dict):
            included_models_list = included_models_config['list']
            invert_check = included_models_config['type'] == 'not'
        else:
            included_models_list = included_models_config

        if len(included_models_list) == 0:
            return not invert_check

        found_car_in_list = False
        for included_model_re in included_models_list:
            if re.search(included_model_re, model_name, re.IGNORECASE):
                found_car_in_list = True
                break

        if invert_check:
            return not found_car_in_list
        else:
            return found_car_in_list

    return False


def is_car_excluded(deal):
    return is_car_in_list(deal, exclusion_list)
