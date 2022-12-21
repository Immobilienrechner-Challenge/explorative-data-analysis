import pandas as pd
import re
import numpy as np


class ImmoHelper(object):
    def __init__(self, url='https://raw.githubusercontent.com/Immobilienrechner-Challenge/data/main/immoscout_cleaned_lat_lon_fixed_v9.csv'):
        self.data = pd.read_csv(url, low_memory=False)
        
    def _parse_floor(self, x):
        if x != x:
          return np.nan
        elif x == 'Ground floor':
          return 0
        elif re.search('\. floor', x):
          return re.search('\d+', x).group()
        elif re.search('Basement', x):
          return '-' + re.search('\d+', x).group()

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

      data_cleaned = pd.DataFrame() 

      # Merge columns
      ## Living Space
      data_cleaned['living_space'] = data['Space extracted'].astype(float)

      ## Rooms
      data_cleaned['rooms'] = data['details_structured'].str.extract('(\d+\.?\d?) rooms').astype(float)

      ## Plot Area
      data_cleaned['plot_area'] = data['Plot_area_merged'].fillna(data['detail_responsive#surface_property'])

      ## Floor Space
      data_cleaned['floor_space'] = data['Floor_space_merged'].fillna(data['detail_responsive#surface_usable'])

      ## Floor
      data_cleaned['floor'] = data['Floor_merged'].fillna(data['detail_responsive#floor'])

      ## Availability
      data_cleaned['availability'] = data['Availability_merged'].fillna(data['detail_responsive#available_from'])

      ## Price
      data_cleaned['price'] = data['price_cleaned']

      ## Zip code
      data_cleaned['zip_code'] = data['address'].str.extract(r'(\d{4}) [A-ZÀ-Ÿ]').astype(int)    
      
      ## Municipality
      data_cleaned['municipality'] = data['address'].str.extract(r'\d{4} (.+?),')
      
      ## Canton
      data_cleaned['canton'] = data['address'].str.extract(r", ?([A-ZÀ-Ÿ]{2})")

      ## Street
      data_cleaned["street"] = data['address'].str.extract(r"(.+), ?\d{4}")
      data_cleaned["street_nr"] = data_cleaned['street'].str.extract(r'^.+ (\d.+)')
      data_cleaned["street"] = data_cleaned['street'].str.extract(r'^(.+?) \d')
      data_cleaned["street"] = data_cleaned['street'].str.rstrip()

      # Parsing
      data_cleaned['plot_area'] = data_cleaned['plot_area'].str.extract('(\d+,?\d*)')
      data_cleaned['plot_area'] = data_cleaned['plot_area'].str.replace(',', '').astype(float)
      data_cleaned['floor_space'] = data_cleaned['floor_space'].str.extract('(\d+,?\d*)')
      data_cleaned['floor_space'] = data_cleaned['floor_space'].str.replace(',', '').astype(float)
      data_cleaned['floor'] = data_cleaned['floor'].apply(self._parse_floor).astype(float)
      data_cleaned['availability'] = data_cleaned['availability']

      # Merge DataFrames
      data_cleaned = data_cleaned.join(data.loc[:, 'ForestDensityL':'type'])
      data_cleaned.drop(['price_cleaned', 'Locality', 'Zip'], axis=1, inplace=True)

      if return_gde:
        return data_cleaned
      else:
        return data_cleaned.drop(data_cleaned.loc[:, 'ForestDensityL':'gde_workers_total'], axis=1)
