import pandas as pd
from sklearn.preprocessing import Normalizer


class ImmoHelper(object):
    def __init__(self, url="https://raw.githubusercontent.com/Immobilienrechner-Challenge/data/main/immoscout_cleaned_lat_lon_fixed_v9.csv", type="csv"):
        self.X = None
        self.y = None
        # Erweiterbar für andere Dateitypen
        if type == "csv":
            self.data = pd.read_csv(url, low_memory=False)

    def process_prediction(self, living_space, type, rooms, gde_tax):
        col = [
            'Living space',
            'rooms',
            'gde_tax',
            'type_attic-flat',
            'type_attic-room',
            'type_castle',
            'type_chalet',
            'type_detached-house',
            'type_detached-secondary-suite',
            'type_duplex-maisonette',
            'type_farmhouse',
            'type_flat',
            'type_furnished-residential-property',
            'type_loft',
            'type_penthouse',
            'type_rustico',
            'type_secondary-suite',
            'type_semi-detached-house',
            'type_single-room',
            'type_stepped-apartment',
            'type_stepped-house',
            'type_studio',
            'type_terrace-house',
            'type_villa'
        ]

        input = {
            "Living space": living_space,
            f"type_{type}": 1,
            "rooms": rooms,
            "gde_tax": gde_tax
        }
        data = pd.DataFrame(input, columns=col, index=[0])
        data = data.fillna(0)
        return data.values

    def process_data(self, data=None):
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
        data["Living space"] = data["Living space"].str.replace(
            "m²", "").astype(float)
        data = pd.get_dummies(data, columns=["type"])
        data = data.dropna()

        # X und y definieren
        y = data["price_cleaned"].values
        X = data.drop(columns=["price_cleaned"]).values

        self.data = data
        self.X = X
        self.y = y
        return self.X, self.y
