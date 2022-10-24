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

    def process_data(self, data=None, return_gde=False):
      """Processes immoscout_cleaned_lat_lon_fixed_v9.csv according to eda findings and returns a tidy dataset. 

      Args:
          data (DataFrame, optional): Uses immoscout_cleaned_lat_lon_fixed_v9.csv if left default. Defaults to None.
          return_gde (bool, optional): Return with or without extra columns ('ForestDensityL':'gde_workers_total'). Defaults to False.

      Returns:
          DataFrame: tidy DataFrame
      """

      if not data:
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
        
      def parse_street(x):
        if len(x) > 0:
          m = re.search(r"\d", x)
          if m:
            return x[0:m.start()-1]
          else:
            return x
        else:
          return np.NaN

      col_names = data.columns.array
      col_names[0:2] = ['Index1', 'Index2']
      data.columns = col_names

      data_cleaned = pd.DataFrame() 

      # Merge columns
      ## Living Space
      data['living_space'] = data['Space extracted']
      # data['details_ls'] = data['details'].str.extract(', (\d+) m').astype(float)
      # data.loc[data['details_ls'].notna() & data['living_space'].isna(), 'living_space'] = data.loc[data['details_ls'].notna() & data['living_space'].isna(), 'details_ls']
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
      data_cleaned["street"] = data['address'].str.extract(r'^([A-Z].+?), ')
      data_cleaned["street_nr"] = data_cleaned['street'].str.extract(r'^.+ (\d.+)')
      data_cleaned["street"] = data_cleaned['street'].fillna('').apply(parse_street)
      data_cleaned["street"] = data_cleaned['street'].str.rstrip()
      data_cleaned[data_cleaned["street"] == 'Lausanne'] = np.NaN
      data_cleaned[data_cleaned["street"] == 'Lugano'] = np.NaN

      ## Zip Code
      data_cleaned['zip_code'] = data['address'].str.extract(r'(\d{4})')
      data_cleaned['zip_code'] = pd.Categorical(data_cleaned['zip_code'])

      ## Canton
      data_cleaned['canton'] = data['address'].str.extract(r'(\w{2})$')
      data_cleaned['canton'] = pd.Categorical(data_cleaned['canton'])

      # Parsing
      data_cleaned['plot_area'] = data_cleaned['plot_area'].replace('', np.nan).str.extract('(\d+,?\d*)')
      data_cleaned['plot_area'] = data_cleaned['plot_area'].str.replace(',', '').astype(float)
      data_cleaned['floor_space'] = data_cleaned['floor_space'].replace('', np.nan).str.extract('(\d+,?\d*)')
      data_cleaned['floor_space'] = data_cleaned['floor_space'].str.replace(',', '').astype(float)
      data_cleaned['floor'] = data_cleaned['floor'].replace('', np.nan).apply(parse_floor).astype(float)
      data_cleaned['availability'] = data_cleaned['availability'].replace('', np.nan)

      # Merge DataFrames
      data_cleaned = data_cleaned.join(data.loc[:, 'ForestDensityL':'type'])
      data_cleaned.drop(['price_cleaned', 'Locality'], axis=1, inplace=True)

      # Drop duplicates and invalid values
      data_cleaned.drop_duplicates(inplace=True)
      data_cleaned.loc[data_cleaned['floor'] >= 100, 'floor'] = np.nan
      data_cleaned.loc[(data_cleaned['living_space'] > 1450) | (data_cleaned['living_space'] < 12), 'living_space'] = np.nan
      data_cleaned.loc[(data_cleaned['plot_area'] > 247330) , 'plot_area'] = np.nan
      data_cleaned.loc[(data_cleaned['price'] < 30000), 'price'] = np.nan

      if return_gde:
        return data_cleaned
      else:
        return data_cleaned.drop(data_cleaned.loc[:, 'ForestDensityL':'gde_workers_total'], axis=1)
