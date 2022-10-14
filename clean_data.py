# import helper functions
from helper import ImmoHelper

helper = ImmoHelper()
df = helper.process_data(return_gde=False)
df.to_csv('../data/clean.csv')

df_gde = helper.process_data(return_gde=True)
df_gde.to_csv('../data/clean_gde.csv')