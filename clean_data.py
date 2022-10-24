# import helper functions
from helper import ImmoHelper
import eda_generate_sweetviz_reports

helper = ImmoHelper()
df = helper.process_data(return_gde=False)
df.to_csv('../data/clean.csv')

df_gde = helper.process_data(return_gde=True)
df_gde.to_csv('../data/clean_gde.csv')

eda_generate_sweetviz_reports.generate_sweetviz_report()