# import helper functions
from helper_new import ImmoHelper
import eda_generate_sweetviz_reports_new

helper = ImmoHelper()
df = helper.process_data(return_gde=False)
df.to_csv("../data/clean_v2.csv")

df_gde = helper.process_data(return_gde=True)
df_gde.to_csv("../data/clean_gde_v2.csv")

eda_generate_sweetviz_reports_new.generate_sweetviz_report()
