import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    'Postcode': {
        'path': os.path.join(BASE_PATH, 'Postcodes', 'POA_2021_AUST_GDA94.shp'),
        'id_column': 'POA_CODE21',
        'name_column': 'POA_NAME21',
        'state_column': 'STE_NAME21'
    },
    'StateElectorate': {
        'path': os.path.join(BASE_PATH, 'StateElectorates', 'SED_2024_AUST_GDA2020.shp'),
        'id_column': 'SED_CODE24',
        'name_column': 'SED_NAME24',
        'state_column': 'STE_NAME21'
    },
    'FederalElectorate': {
        'path': os.path.join(BASE_PATH, 'FederalElectorates', 'CED_2021_AUST_GDA2020.shp'),
        'id_column': 'CED_CODE21',
        'name_column': 'CED_NAME21',
        'state_column': 'STE_NAME21'
    },
    'State': {
        'path': os.path.join(BASE_PATH, 'States', 'STE_2021_AUST_GDA2020.shp'),
        'id_column': 'STE_CODE21',
        'name_column': 'STE_NAME21',
    },
    'postcode_ranges' : {
                'New South Wales': [(1000, 2599), (2619, 2899), (2921, 2999)],
                'Australian Capital Territory': [(2600, 2618), (2900, 2920)],
                'Victoria': [(3000, 3999)],
                'Queensland': [(4000, 4999), (9000, 9999)],
                'South Australia': [(5000, 5999)],
                'Western Australia': [(6000, 6797), (6800, 6999)],
                'Tasmania': [(7000, 7999)],
                'Northern Territory': [(800, 899)], 
                'Overall': [(200, 9999)]
            }
}
