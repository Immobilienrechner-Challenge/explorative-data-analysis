import pandas as pd
import re
import numpy as np


class ImmoHelper(object):
    def __init__(
        self,
        url="https://github.com/Immobilienrechner-Challenge/data/blob/main/immo_data_202208_v2.parquet?raw=true",
        type="parquet",
    ):
        self.X = None
        self.y = None
        # Erweiterbar für andere Dateitypen
        if type == "csv":
            self.data = pd.read_csv(url, low_memory=False)
        if type == "parquet":
            self.data = pd.read_parquet(url)

    def process_data(self, data=None, return_gde=False):
        """Processes immo_data_202208_v2 according to eda findings and returns a tidy dataset.

        Args:
            data (DataFrame, optional): Uses immo_data_202208_v2 if left default. Defaults to None.
            return_gde (bool, optional): Return with or without extra columns ('ForestDensityL':'gde_workers_total'). Defaults to False.

        Returns:
            DataFrame: tidy DataFrame
        """

        if not data:
            data = self.data.copy()

        def parse_floor(x):
            if x != x:
                return np.nan
            elif x == "Ground floor":
                return 0
            elif re.search("\. floor", x):
                return re.search("\d+", x).group()
            elif re.search("Basement", x):
                return "-" + re.search("\d+", x).group()

        col_names = data.columns.array
        col_names[0:2] = ["Index1", "Index2"]
        data.columns = col_names

        data_cleaned = pd.DataFrame()

        # Merge columns
        ## Living Space
        data["living_space"] = data["Living_area_unified"]
        data_cleaned["living_space"] = data["living_space"].astype(float)

        ## Rooms
        # data_cleaned["rooms"] = (
        #    data["details"].str.extract("(\d+\.?\d?) rooms, ").astype(float)
        # )
        data_cleaned["rooms"] = data["rooms"].str.replace("rm", "").astype(float)

        ## Plot Area
        data_cleaned["plot_area"] = data["Plot_area_merged"].fillna("") + data[
            "detail_responsive#surface_property"
        ].fillna("")

        ## Floor Space
        data_cleaned["floor_space"] = data["Floor_space_merged"].fillna("") + data[
            "detail_responsive#surface_usable"
        ].fillna("")

        ## Floor
        data_cleaned["floor"] = data["Floor_merged"].fillna("") + data[
            "detail_responsive#floor"
        ].fillna("")

        ## Availability
        data_cleaned["availability"] = data["Availability_merged"].fillna("") + data[
            "detail_responsive#available_from"
        ].fillna("")

        ## Price
        # data_cleaned["price"] = data["price_cleaned"]

        ## Municipality
        data_cleaned["municipality"] = data["Locality"]

        ## Street
        data_cleaned["street"] = data["location_parsed"].str.extract(
            r"^Strasse: ?(.+?) plz"
        )
        data_cleaned["street"] = data_cleaned["street"].replace(" ", np.nan)

        data_cleaned["street_nr"] = data_cleaned["street"].str.extract(r"^.+ (\d.+)")
        # separate street name from street number
        data_cleaned["street"] = data_cleaned["street"].str.extract(r"^(.+?) \d")
        data_cleaned["street"] = data_cleaned["street"].str.rstrip()

        ## Zip Code
        data_cleaned["zip_code"] = data["location_parsed"].str.extract(r"plz: ?(\d{4})")
        data_cleaned["zip_code"] = pd.Categorical(data_cleaned["zip_code"])

        ## Canton
        data_cleaned["canton"] = data["location_parsed"].str.extract(
            r"Kanton: ?(\w{2})$"
        )
        data_cleaned["canton"] = pd.Categorical(data_cleaned["canton"])

        # type
        data_cleaned["type"] = data["type_unified"]

        # Parsing
        data_cleaned["plot_area"] = (
            data_cleaned["plot_area"].replace("", np.nan).str.extract("(\d+,?\d*)")
        )
        data_cleaned["plot_area"] = (
            data_cleaned["plot_area"].str.replace(",", "").astype(float)
        )
        data_cleaned["floor_space"] = (
            data_cleaned["floor_space"].replace("", np.nan).str.extract("(\d+,?\d*)")
        )
        data_cleaned["floor_space"] = (
            data_cleaned["floor_space"].str.replace(",", "").astype(float)
        )
        data_cleaned["floor"] = (
            data_cleaned["floor"].replace("", np.nan).apply(parse_floor).astype(float)
        )
        data_cleaned["availability"] = data_cleaned["availability"].replace("", np.nan)

        # Merge DataFrames
        data_cleaned = data_cleaned.join(
            data.loc[:, "ForestDensityL":"gde_workers_total"]
        )
        data_cleaned.drop(["Locality"], axis=1, inplace=True)

        # Drop duplicates and invalid values
        data_cleaned.drop_duplicates(inplace=True)
        data_cleaned.loc[data_cleaned["floor"] >= 100, "floor"] = np.nan
        data_cleaned.loc[
            (data_cleaned["living_space"] > 1450) | (data_cleaned["living_space"] < 12),
            "living_space",
        ] = np.nan
        data_cleaned.loc[(data_cleaned["plot_area"] > 247330), "plot_area"] = np.nan
        # data_cleaned.loc[(data_cleaned["price"] < 30000), "price"] = np.nan

        if return_gde:
            return data_cleaned
        else:
            return data_cleaned.drop(
                data_cleaned.loc[:, "ForestDensityL":"gde_workers_total"], axis=1
            )
