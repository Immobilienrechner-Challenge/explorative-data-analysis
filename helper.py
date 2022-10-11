import pandas as pd
from sklearn.model_selection import train_test_split


class ImmoHelper(object):
    def __init__(self, url="https://raw.githubusercontent.com/Immobilienrechner-Challenge/data/main/immoscout_cleaned_lat_lon_fixed_v9.csv", type="csv"):
        # Erweiterbar für andere Dateitypen
        if type == "csv":
            self.data = pd.read_csv(url, low_memory=False)

    def process_data(self):
        data = self.data.copy()
        # Nur relevante Spalten selektieren
        cols = [
            "price_cleaned",
            "Living space",
            "type",
            "rooms",
            "gde_tax"
        ]
        data = data[cols]

        # Relevante Spalten verarbeiten
        data["Living space"] = data["Living space"].str.replace("m²", "").astype(float)
        data = pd.get_dummies(data["type"])
        data = data.dropna()

        self.data = data.copy()
        return self.data
