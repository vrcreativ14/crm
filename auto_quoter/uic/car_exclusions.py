"""Data and methods that are used to check if a car is an excluded or referral required model
for UIC."""
import re

# When checking the exclusion and blacklists, we try a full match with the make name. For the models:
# - If the list is empty, all models from the make are included in the list
# - Otherwise each item in the list is used as a regex to match against the model name. Any match means the given model
#   is excluded

exclusion_list = {
    'audi': [r'^A', r'^Q'],
    'bentley': [],
    'bmw': [r'^125i', '^225i', '^3.0i', '^220i', 'cabrio', 'alpina', '^i8', '^235'],
    'chevrolet': [r'camaro', r'silverado', 'avalanche', 'colorado', 'luv'],
    'ferrari': [],
    'ford': [r'150', r'250', r'450'],
    'gmc': [r'sierra'],
    'hummer': [],
    'hyundai': [r'coupe', r'elantra', r'veloster'],
    'infiniti': [r'^G.*(sport|coupe)', r'^M', r'^Q60'],
    'jaguar': [],
    'jeep': [r'Wrangler'],
    'lexus': [r'^CT', r'^IS', r'430', r'^RC350'],
    'lincoln': [],
    'maybach': [],
    'maserati': [],
    'mercedes-benz': [r'^C', r'^CL', r'^SLR', r'^SLS', r'AMG', r'^E350', r'^G500', r'GT Sport'],
    'porsche': {'type': 'not',
                'list': [r'Cayenne', r'Macan']},
    'rolls-royce': [],
    'toyota': [r'Tundra', r'Tacoma']
}

blacklist = {
    'audi': [r'^R', '^S', '^TT'],
    'bmw': [r'^130i', r'^135i', r'^6', r'^M', r'^Z'],
    'cadillac': {'type': 'not',
                 'list': [r'Escalade']},
    'chevrolet': [r'Corvette', r'Caprice SS', r'CR8', r'Lumina S', r'Lumina SS'],

    'dodge': [r'Charger', r'Challenger', r'Viper'],
    'ram': [],

    'ford': [r'Mustang', r'Thunderbird'],
    'jeep': [r'Grand Cherokee.*SRT', r'Grand Cherokee 5', r'Grand Cherokee 6'],
    'mazda': [r'Sport'],
    'mercedes-benz': [r'^A', r'^B'],
    'mitsubishi': [r'Eclipse', r'COLT', r'Evolution'],
    'nissan': [r'Titan', r'ZX', r'240', r'GT-R', r'\d+Z', r'Maxima'],
    'peugeot': [r'^206\s?CC', r'^207\s?CC', r'^207\s?RC', r'^207 Sportium', r'^307\s?CC', r'^308\s?CC', r'^407.*Coupe',
                r'RCZ', r'Sport'],
    'suzuki': [r'Swift'],
    'toyota': [r'86', r'Solara', r'Zelas'],
    'volkswagen': [r'^Golf', r'^CC', r'^Beetle', r'^Rabbit', r'^Scirocco', r'EOS'],

    'alfa romeo': [],
    'aston martin': [],
    'brilliance': [],
    'bugatti': [],
    'chery': [],
    'chrysler': [],
    'cmc': [],
    'changan': [],
    'fiat': [],
    'fisker': [],
    'gac': [],
    'geely': [],
    'great wall': [],
    'jac': [],
    'lamborghini': [],
    'lotus': [],
    'luxgen': [],
    'mclaren': [],
    'mini': [],
    'mg': [],
    'morgan': [],
    'opel': [],
    'proton': [],
    'renault': [],
    'saab': [],
    'škoda': [],
    'seat': [],
    'ssangyong': [],
    'subaru': [],
    'volvo': [],
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


def is_car_black_listed(deal):
    return is_car_in_list(deal, blacklist)
