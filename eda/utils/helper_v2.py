import pandas as pd
import re
import numpy as np

class ImmoHelper(object):
    def __init__(self, url='https://github.com/Immobilienrechner-Challenge/data/blob/main/immo_data_202208_v2.parquet?raw=true'):
        self.data = pd.read_parquet(url)
        
    def _parse_floor(self, x):
        if x != x:
          return np.nan
        elif x == 'Ground floor':
          return 0
        elif re.search('\. floor', x):
          return re.search('\d+', x).group()
        elif re.search('Basement', x):
          return '-' + re.search('\d+', x).group()

    def process_data(self, data=None, return_gde=False, kaggle=False):
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
      data_cleaned['living_space'] = data['Space extracted']

      ## Rooms
      data_cleaned['rooms'] = data['details_structured'].str.extract('(\d+\.?\d?) rooms').astype(float)
      data_cleaned['rooms'] = data_cleaned['rooms'].fillna(data['No. of rooms:'])

      ## Plot Area
      data_cleaned['plot_area'] = data['Plot_area_merged'].fillna('') + \
        data['detail_responsive#surface_property'].fillna('')
      data_cleaned['plot_area'] = data_cleaned['plot_area'].fillna(data['Land area:'])
    
      ## Floor Space
      data_cleaned['floor_space'] = data['Floor_space_merged'].fillna('') + \
        data['detail_responsive#surface_usable'].fillna('')
      data_cleaned['floor_space'] = data_cleaned['floor_space'].fillna(data['Floor space:'])

      ## Floor
      data_cleaned['floor'] = data['Floor_merged'].fillna('') + \
        data['detail_responsive#floor'].fillna('')
      data_cleaned['floor'] = data_cleaned['floor'].fillna(data['Floor']).replace('', np.nan)

      ## Availability
      data_cleaned['availability'] = data['Availability_merged'].fillna('') + \
        data['detail_responsive#available_from'].fillna('')

      ## Price
      if not kaggle:
          data_cleaned['price'] = data['price_cleaned']

      ## zip code
      data_cleaned['zip_code'] = data['address'].str.extract(r'(\d{4}) [A-ZÀ-Ÿ]') 
      data_cleaned['zip_address_s'] = data['address_s'].str.extract("(\d{4}) [A-ZÀ-Ÿ]")
      data_cleaned['zip_code'] = data_cleaned['zip_code'].fillna(data_cleaned['zip_address_s']) 
      # drop where zip_code is na
      data_cleaned.dropna(subset=['zip_code'], inplace=True)

      # clean up typos
      data_cleaned.loc[data_cleaned['zip_code'] == '2737', 'zip_code'] = '2735'
      data_cleaned.loc[data_cleaned['zip_code'] == '3217', 'zip_code'] = '3127'
      data_cleaned.loc[data_cleaned['zip_code'] == '3364', 'zip_code'] = '3365'
      

      data_cleaned['municipality'] = data['address'].str.extract(r'\d{4} (.+?),')
      data_cleaned['municipality_address_s'] = data['address_s'].str.extract(r"\d{4} (.+)$")
      data_cleaned['municipality'] = data_cleaned['municipality'].fillna(data_cleaned['municipality_address_s'])
      
      df_xlsx_plz = pd.read_excel("./utils/plz.xlsx", sheet_name='Blatt1')
      df_xlsx_plz.drop(['Kanton', 'Canton', 'Cantone', 'Land', 'Pays', 'Paese'], axis=1, inplace=True)
      df_xlsx_plz.rename(columns={df_xlsx_plz.columns[0]: 'plz', df_xlsx_plz.columns[1]: 'municipality', df_xlsx_plz.columns[2]: 'canton'}, inplace=True)
      df_xlsx_plz.drop_duplicates(subset=['plz'], inplace=True)

      data_cleaned['canton'] = data_cleaned['zip_code'].astype(int).map(df_xlsx_plz.set_index('plz')['canton']).copy()
      
      # Clean up cantons
      data_cleaned.loc[data_cleaned['zip_code'] == '1919', 'canton'] = 'VS'
      data_cleaned.loc[data_cleaned['zip_code'] == '1818', 'canton'] = 'VD'

      ## Street
      data_cleaned["street"] = data['address'].str.extract(r"(.+), \d{4}")
      data_cleaned.loc[data_cleaned['street'] == '-', 'street'] = np.nan
      data_cleaned.loc[data_cleaned['street'] == 'à', 'street'] = np.nan


      data_cleaned["street_nr"] = data_cleaned['street'].str.extract(r'^.+ (\d.+)')
      
      # separate street name from street number
      data_cleaned["street"] = data_cleaned['street'].str.extract(r'^(.+?) \d')
      data_cleaned["street"] = data_cleaned['street'].str.rstrip()

      # Parsing
      data_cleaned['plot_area'] = data_cleaned['plot_area'].replace('', np.nan).str.extract('(\d+,?\d*)')
      data_cleaned['plot_area'] = data_cleaned['plot_area'].str.replace(',', '').astype(float)
      data_cleaned['living_space'] = data_cleaned['living_space'].astype(float)
      data_cleaned['floor_space'] = data_cleaned['floor_space'].replace('', np.nan).str.extract('(\d+,?\d*)')
      data_cleaned['floor_space'] = data_cleaned['floor_space'].str.replace(',', '').astype(float)
      data_cleaned['floor'] = data_cleaned['floor'].apply(self._parse_floor).astype(float)
      data_cleaned['availability'] = data_cleaned['availability'].replace('', np.nan)

      # Merge DataFrames
      cols_to_join = ['type_unified', 'features', 'Last refurbishment:', 'Year built:']
      data_cleaned = data_cleaned.join(data[cols_to_join])
      data_cleaned.rename(columns={'type_unified': 'type', 'Last refurbishment:': 'last_refurbishment', 'Year built:': 'year_built'}, inplace=True)
      data_cleaned.drop(['municipality_address_s', 'zip_address_s'], axis=1, inplace=True)

      if return_gde:
        return data_cleaned.join(data.loc[:, 'ForestDensityL':'gde_workers_total'])
      else:
        return data_cleaned