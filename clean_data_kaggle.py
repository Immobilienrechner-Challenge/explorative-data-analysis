# import helper functions
from helper_kaggle import ImmoHelper
import eda_generate_sweetviz_reports_new

helper = ImmoHelper(url="../data/kaggle_uncleaned.csv", type="csv")
df = helper.process_data(return_gde=False)
df.to_csv("../data/kaggle_cleaned.csv")

df_gde = helper.process_data(return_gde=True)
df_gde.to_csv("../data/kaggle_gde_cleaned.csv")

# eda_generate_sweetviz_reports_new.generate_sweetviz_report()
