import pandas as pd
from sklearn.preprocessing import Normalizer

class ImmoHelper(object):
    def __init__(self, url="https://raw.githubusercontent.com/Immobilienrechner-Challenge/data/main/immoscout_cleaned_lat_lon_fixed_v9.csv", type="csv"):
        self.X = None
        self.y = None
        # Erweiterbar für andere Dateitypen
        if type == "csv":
            self.data = pd.read_csv(url, low_memory=False)

    def process_data(self, data = None):
        if data == None:
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
        data = pd.get_dummies(data, columns=["type"])
        data = data.dropna()

        # X und y definieren und X normalisieren
        y = data["price_cleaned"].values
        X = data.drop(columns = ["price_cleaned"]).values
        X = Normalizer().transform(X)

        self.data = data
        self.X = X
        self.y = y
        return self.X, self.y
