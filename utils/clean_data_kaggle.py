# import helper functions
from helper_kaggle import ImmoHelper

helper = ImmoHelper(url="../data/kaggle_uncleaned.csv", type="csv")
helper.data.to_parquet("../data/kaggle_uncleaned.parquet")

df = helper.process_data(return_gde=False)
df.to_parquet("../data/kaggle_cleaned.parquet")

df_gde = helper.process_data(return_gde=True)
df_gde.to_parquet("../data/kaggle_gde_cleaned.parquet")
