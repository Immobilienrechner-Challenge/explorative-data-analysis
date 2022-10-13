import pandas as pd
import re
import numpy as np
from sklearn.preprocessing import Normalizer


class ImmoHelper(object):
    def __init__(self, url="https://raw.githubusercontent.com/Immobilienrechner-Challenge/data/main/immoscout_cleaned_lat_lon_fixed_v9.csv", type="csv"):
        self.X = None
        self.y = None
        # Erweiterbar für andere Dateitypen
        if type == "csv":
            self.data = pd.read_csv(url, low_memory=False)

    def process_prediction(self, living_space, type, rooms, gde_tax):
        col = [
            'Living space',
            'rooms',
            'gde_tax',
            'type_attic-flat',
            'type_attic-room',
            'type_castle',
            'type_chalet',
            'type_detached-house',
            'type_detached-secondary-suite',
            'type_duplex-maisonette',
            'type_farmhouse',
            'type_flat',
            'type_furnished-residential-property',
            'type_loft',
            'type_penthouse',
            'type_rustico',
            'type_secondary-suite',
            'type_semi-detached-house',
            'type_single-room',
            'type_stepped-apartment',
            'type_stepped-house',
            'type_studio',
            'type_terrace-house',
            'type_villa'
        ]

        input = {
            "Living space": living_space,
            f"type_{type}": 1,
            "rooms": rooms,
            "gde_tax": gde_tax
        }
        data = pd.DataFrame(input, columns=col, index=[0])
        data = data.fillna(0)
        return data.values

    def process_data(self, data=None):
        if data == None:
            data = self.data.copy()

        def parse_floor(x):
          if x != x:
            return np.nan
          elif x == 'Ground floor':
            return 0
          elif re.search('\. floor', x):
            return re.search('\d+', x).group()
          elif re.search('Basement', x):
            return '-' + re.search('\d+', x).group()

        col_names = data.columns.array
        col_names[0:2] = ['Index1', 'Index2']
        data.columns = col_names

        data_cleaned = pd.DataFrame()

        # Merge columns
        ## Living Space
        data['living_space'] = data['Space extracted']
        data['details_ls'] = data['details'].str.extract(', (\d+) m').astype(float)
        data.loc[data['details_ls'].notna() & data['living_space'].isna(), 'living_space'] = data.loc[data['details_ls'].notna() & data['living_space'].isna(), 'details_ls']
        data_cleaned['living_space'] = data['living_space'].astype(float)

        ## Rooms
        data_cleaned['rooms'] = data['details'].str.extract('(\d+\.?\d?) rooms, ').astype(float)

        ## Plot Area
        data_cleaned['plot_area'] = data['Plot_area_merged'].fillna('') + \
          data['detail_responsive#surface_property'].fillna('')

        ## Floor Space
        data_cleaned['floor_space'] = data['Floor_space_merged'].fillna('') + \
          data['detail_responsive#surface_usable'].fillna('')

        ## FLoor
        data_cleaned['floor'] = data['Floor_merged'].fillna('') + \
          data['detail_responsive#floor'].fillna('')

        ## Availability
        data_cleaned['availability'] = data['Availability_merged'].fillna('') + \
          data['detail_responsive#available_from'].fillna('')

        ## Price
        data_cleaned['price'] = data['price_cleaned']

        ## Municipality
        data_cleaned['municipality'] = data['Locality']

        ## Street
        data_cleaned["street"] = data['address'].str.extract(r'(.+?),')
        data_cleaned['street'] = data_cleaned['street'].str.replace(r'^\d+\s\w+', 'NaN')

        ## Zip Code
        data_cleaned['zip_code'] = data['address'].str.extract(r'(\d{4})')

        ## Canton
        data_cleaned['canton'] = data['address'].str.extract(r'(\w{2})$')

        # Parsing
        data_cleaned['plot_area'] = data_cleaned['plot_area'].replace('', np.nan).str.extract('(\d+)').astype(float)
        data_cleaned['floor_space'] = data_cleaned['floor_space'].replace('', np.nan).str.extract('(\d+)').astype(float)
        data_cleaned['floor'] = data_cleaned['floor'].replace('', np.nan).apply(parse_floor).astype(float)
        data_cleaned['availability'] = data_cleaned['availability'].replace('', np.nan)
        data_cleaned = data_cleaned.join(data.loc[:, 'ForestDensityL':'type'])
        data_cleaned.drop('price_cleaned', axis=1, inplace=True)
        # # Nur relevante Spalten selektieren
        # cols = [
        #     "price_cleaned",
        #     "Living space",
        #     "type",
        #     "rooms",
        #     "gde_tax"
        # ]
        # data = data[cols]

        # # Relevante Spalten verarbeiten
        # data["Living space"] = data["Living space"].str.replace(
        #     "m²", "").astype(float)
        # data = pd.get_dummies(data, columns=["type"])
        # data = data.dropna()

        # X und y definieren
        y = data_cleaned["price"].values
        X = data_cleaned.drop(columns=["price"]).values

        self.data = data_cleaned
        self.X = X
        self.y = y
        return self.X, self.y


    def drop_cols(self):
        '''
        This Method is dropping all the unnecessary columns
        from our raw DataFrame. 
        The selected columns for dropping can be find  in this
        excel sheet marked as red. 
        https://github.com/Immobilienrechner-Challenge/explorative-data-analysis/blob/main/columns.xlsx
        '''
        cols_to_drop = ['Unnamed: 0', 'Unnamed: 0.1', 'Municipality', 'Living space', \
                        'Plot area', 'Floor space', 'Availability', 'location', 'description', \
                        'url', 'table', 'Floor', 'detail_responsive#municipality', \
                        'detail_responsive#surface_living', 'detail_responsive#floor', \
                        'detail_responsive#available_from', 'Gemeinde', 'Wohnfläche', \
                        'Stockwerk', 'Nutzfläche', 'Verfügbarkeit', 'Grundstücksfläche',
                        'detail_responsive#surface_property', \
                        'detail_responsive#surface_usable', 'Commune', 'Surface habitable', \
                        'Surface du terrain', 'Surface utile', 'Disponibilité', 'Étage', \
                        'Comune', 'Superficie abitabile', 'Disponibilità', 'Gross return', \
                        'Piano', 'Superficie del terreno', 'Superficie utile', \
                        'Municipality_merged', 'Floor_merged', 'Living_space_merged', \
                        'Floor_space_merged', 'Plot_area_merged', 'Availability_merged', \
                        'location_parsed', 'title', 'details', 'price', 'link', 'details_structured', \
                        'lon', 'lat', 'index', 'Space extracted', 'rooms']

        self.data.drop(cols_to_drop, axis=1, inplace=True)
        return self

class dropper():

  def drop(self, data):
    '''
    This Method is dropping all the unnecessary columns
    from our raw DataFrame. 
    The selected columns for dropping can be find  in this
    excel sheet marked as red.
    '''
    # Create list of columns to drop
    cols_to_drop = ['Unnamed: 0', 'Unnamed: 0.1', 'Municipality', 'Living space', \
                    'Plot area', 'Floor space', 'Availability', 'location', 'description', \
                    'table', 'Floor', 'detail_responsive#municipality', \
                    'detail_responsive#surface_living', 'detail_responsive#floor', \
                    'detail_responsive#available_from', 'Gemeinde', 'Wohnfläche', \
                    'Stockwerk', 'Nutzfläche', 'Verfügbarkeit', 'Grundstücksfläche',
                    'detail_responsive#surface_property', \
                    'detail_responsive#surface_usable', 'Commune', 'Surface habitable', \
                    'Surface du terrain', 'Surface utile', 'Disponibilité', 'Étage', \
                    'Comune', 'Superficie abitabile', 'Disponibilità', 'Gross return', \
                    'Piano', 'Superficie del terreno', 'Superficie utile', \
                    'Municipality_merged', 'Floor_merged', 'Living_space_merged', \
                    'Floor_space_merged', 'Plot_area_merged', 'Availability_merged', \
                    'location_parsed', 'title', 'details', 'price', 'link', 'details_structured', \
                    'lon', 'lat', 'index', 'Space extracted', 'rooms']

    # Drop columns
    data.drop(cols_to_drop, axis=1, inplace=True)

    # Return data
    return data
