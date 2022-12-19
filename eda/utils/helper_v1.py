import pandas as pd
import re
import numpy as np
from sklearn.preprocessing import Normalizer


class ImmoHelper(object):
    def __init__(self, url='https://raw.githubusercontent.com/Immobilienrechner-Challenge/data/main/immoscout_cleaned_lat_lon_fixed_v9.csv', type="csv"):
        self.X = None
        self.y = None
        # Erweiterbar für andere Dateitypen
        if type == "csv":
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

      col_names = data.columns.array
      col_names[0:2] = ['Index1', 'Index2']
      data.columns = col_names

      data_cleaned = pd.DataFrame() 

      # Merge columns
      ## Living Space
      data['living_space'] = data['Space extracted']
      data_cleaned['living_space'] = data['living_space'].astype(float)

      ## Rooms
      data_cleaned['rooms'] = data['details_structured'].str.extract('(\d+\.?\d?) rooms').astype(float)

      ## Plot Area
      data_cleaned['plot_area'] = data['Plot_area_merged'].fillna('') + \
        data['detail_responsive#surface_property'].fillna('')

      ## Floor Space
      data_cleaned['floor_space'] = data['Floor_space_merged'].fillna('') + \
        data['detail_responsive#surface_usable'].fillna('')

      ## Floor
      data_cleaned['floor'] = data['Floor_merged'].fillna('') + \
       data['detail_responsive#floor'].fillna('')

      ## Availability
      data_cleaned['availability'] = data['Availability_merged'].fillna('') + \
        data['detail_responsive#available_from'].fillna('')

      ## Price
      data_cleaned['price'] = data['price_cleaned']

      ## zip code
      df_xlsx_plz = pd.read_excel("./utils/plz.xlsx", sheet_name='Blatt1')
      df_xlsx_plz.drop(['Kanton', 'Canton', 'Cantone', 'Land', 'Pays', 'Paese'], axis=1, inplace=True)
      df_xlsx_plz.rename(columns={df_xlsx_plz.columns[0]: 'plz', df_xlsx_plz.columns[1]: 'municipality', df_xlsx_plz.columns[2]: 'kanton'}, inplace=True)

      data_cleaned['zip_code'] = data['address'].str.extract(r'(\d{4})').astype(int)
      data_cleaned['plz_from_location_parsed'] = data['location_parsed'].str.extract(r'plz:(\d+)')
      data_cleaned.loc[~data_cleaned['zip_code'].isin(df_xlsx_plz['plz']), 'zip_code'] = data_cleaned.loc[~data_cleaned['zip_code'].isin(df_xlsx_plz['plz']), 'plz_from_location_parsed'].values
      data_cleaned['zip_code'] = data_cleaned['zip_code'].astype(int)
      
      df_xlsx_plz.drop_duplicates(subset='plz', inplace=True)
      data_cleaned['municipality'] = data_cleaned['zip_code'].map(df_xlsx_plz.set_index('plz')['municipality'])
      data_cleaned['canton'] = data_cleaned['zip_code'].map(df_xlsx_plz.set_index('plz')['kanton'])


      ## Street
      data_cleaned["street"] = data['location_parsed'].str.extract(r'^Strasse: ?(.+?) plz')
      data_cleaned["street_from_address"] = data['address'].str.extract(r'(.+), \d{4}')
      data_cleaned["street"] = data_cleaned["street"].replace(' ', np.nan)
      data_cleaned.loc[data_cleaned['street_from_address'] == '-', 'street_from_address'] = np.nan
      data_cleaned.loc[data_cleaned['street'] == '-', 'street'] = np.nan
      data_cleaned.loc[data_cleaned['street'].isna(), 'street'] = data_cleaned.loc[data_cleaned['street'].isna(), 'street_from_address'].values
      data_cleaned.loc[data_cleaned['street'] == 'à', 'street'] = np.nan
      data_cleaned.loc[12363, 'street'] = 'Rte de la Jorette'


      


      data_cleaned["street_nr"] = data_cleaned['street'].str.extract(r'^.+ (\d.+)')
      
      # separate street name from street number
      data_cleaned["street"] = data_cleaned['street'].str.extract(r'^(.+?) \d')
      data_cleaned["street"] = data_cleaned['street'].str.rstrip()

      # Parsing
      data_cleaned['plot_area'] = data_cleaned['plot_area'].replace('', np.nan).str.extract('(\d+,?\d*)')
      data_cleaned['plot_area'] = data_cleaned['plot_area'].str.replace(',', '').astype(float)
      data_cleaned['floor_space'] = data_cleaned['floor_space'].replace('', np.nan).str.extract('(\d+,?\d*)')
      data_cleaned['floor_space'] = data_cleaned['floor_space'].str.replace(',', '').astype(float)
      data_cleaned['floor'] = data_cleaned['floor'].replace('', np.nan).apply(self._parse_floor).astype(float)
      data_cleaned['availability'] = data_cleaned['availability'].replace('', np.nan)

      # Merge DataFrames
      data_cleaned = data_cleaned.join(data.loc[:, 'ForestDensityL':'type'])
      data_cleaned.drop(['price_cleaned', 'Locality', 'Zip', 'plz_from_location_parsed', 'street_from_address'], axis=1, inplace=True)

      # Drop duplicates and invalid values
      data_cleaned.drop_duplicates(inplace=True)
      data_cleaned.drop(3874, inplace=True)
      data_cleaned.loc[data_cleaned['floor'] >= 100, 'floor'] = np.nan
      data_cleaned.loc[(data_cleaned['living_space'] > 1450) | (data_cleaned['living_space'] < 12), 'living_space'] = np.nan
      data_cleaned.loc[(data_cleaned['plot_area'] > 247330) , 'plot_area'] = np.nan
      data_cleaned.loc[(data_cleaned['price'] < 30000), 'price'] = np.nan

      if return_gde:
        return data_cleaned
      else:
        return data_cleaned.drop(data_cleaned.loc[:, 'ForestDensityL':'gde_workers_total'], axis=1)
