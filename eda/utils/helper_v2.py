import pandas as pd
import re
import numpy as np


class ImmoHelper(object):
    def __init__(
        self,
        url="https://github.com/Immobilienrechner-Challenge/data/blob/main/immo_data_202208_v2.parquet?raw=true",
    ):
        self.data = pd.read_parquet(url)

    def _parse_floor(self, x):
        if x != x:
            return np.nan
        elif x == "Ground floor":
            return 0
        elif re.search("\. floor", x):
            return re.search("\d+", x).group()
        elif re.search("Basement", x):
            return "-" + re.search("\d+", x).group()

    def process_data(self, data=None, return_gde=False, kaggle=False):
        """Processes immo_data_202208_v2.parquet according to eda findings and returns a tidy dataset.

        Args:
            data (DataFrame, optional): Uses immo_data_202208_v2.parquet if left default. Defaults to None.
            return_gde (bool, optional): Return with or without extra columns ('ForestDensityL':'gde_workers_total'). Defaults to False.

        Returns:
            DataFrame: tidy DataFrame
        """

        if not data:
            data = self.data.copy()

        data_cleaned = pd.DataFrame()

        # Merge columns
        ## Living Space
        data_cleaned["living_space"] = data["Living_area_unified"].astype(float)
        data_cleaned["living_space"] = data_cleaned["living_space"].fillna(
            data["Space extracted"]
        )

        ## Rooms
        data_cleaned["rooms"] = data["rooms"].str.replace("rm", "").astype(float)
        data_cleaned["rooms"] = data_cleaned["rooms"].fillna(
            data["No. of rooms:"].astype(float)[0]
        )

        ## Plot Area
        data_cleaned["plot_area"] = (
            data["Plot_area_merged"]
            .fillna(data["detail_responsive#surface_property"])
            .fillna(data["Land area:"])
        )

        ## Floor Space
        data_cleaned["floor_space"] = (
            data["Floor_space_merged"]
            .fillna(data["detail_responsive#surface_usable"])
            .fillna(data["Floor space:"])
        )

        ## Floor
        data_cleaned["floor"] = (
            data["Floor_merged"]
            .fillna(data["detail_responsive#floor"])
            .fillna(data["Floor"])
            .fillna("")
            .replace("", np.nan)
        )

        ## Availability
        data_cleaned["availability"] = data["Availability_merged"].fillna(
            data["detail_responsive#available_from"]
        )

        ## Price
        if not kaggle:
            data_cleaned["price"] = data["price_cleaned"]

        ## Zip code
        data_cleaned["zip_code"] = data["address"].str.extract(r"(\d{4}) [A-ZÀ-Ÿa-z]")
        data_cleaned["zip_address_s"] = data["address_s"].str.extract(
            "(\d{4}) [A-ZÀ-Ÿa-z]"
        )
        data_cleaned["zip_code"] = data_cleaned["zip_code"].fillna(
            data_cleaned["zip_address_s"]
        )

        # if not kaggle:
        # Clean up typos
        data_cleaned.loc[data_cleaned["zip_code"] == "2737", "zip_code"] = "2735"
        data_cleaned.loc[data_cleaned["zip_code"] == "3217", "zip_code"] = "3127"
        data_cleaned.loc[data_cleaned["zip_code"] == "3364", "zip_code"] = "3365"
        data_cleaned.loc[data_cleaned["zip_code"] == "6511", "zip_code"] = "6593"
        data_cleaned.loc[data_cleaned["zip_code"] == "8371", "zip_code"] = "8370"

        data_cleaned["municipality"] = data["address"].str.extract(r"\d{4} (.+?),")
        data_cleaned["municipality_address_s"] = data["address_s"].str.extract(
            r"\d{4} (.+)$"
        )
        data_cleaned["municipality"] = data_cleaned["municipality"].fillna(
            data_cleaned["municipality_address_s"]
        )

        ## Canton
        df_xlsx_plz = pd.read_excel(
            "https://github.com/Immobilienrechner-Challenge/data/raw/main/plz.xlsx",
            sheet_name="Blatt1",
        )
        df_xlsx_plz.drop(
            ["Kanton", "Canton", "Cantone", "Land", "Pays", "Paese"],
            axis=1,
            inplace=True,
        )
        df_xlsx_plz.rename(
            columns={
                df_xlsx_plz.columns[0]: "plz",
                df_xlsx_plz.columns[1]: "municipality",
                df_xlsx_plz.columns[2]: "canton",
            },
            inplace=True,
        )
        df_xlsx_plz.drop_duplicates(subset=["plz"], inplace=True)

        data_cleaned["canton"] = (
            data_cleaned["zip_code"]
            .fillna(0)
            .astype(int)
            .map(df_xlsx_plz.set_index("plz")["canton"])
            .copy()
        )

        ## Street
        data_cleaned["street"] = data["address"].str.extract(r"(.+), \d{4}")
        data_cleaned["street_nr"] = data_cleaned["street"].str.extract(r"^.+ (\d.+)")
        data_cleaned["street"] = data_cleaned["street"].str.extract(r"^(.+?) \d")
        data_cleaned["street"] = data_cleaned["street"].str.rstrip()

        # Parsing
        data_cleaned["plot_area"] = data_cleaned["plot_area"].str.extract("(\d+,?\d*)")
        data_cleaned["plot_area"] = (
            data_cleaned["plot_area"].str.replace(",", "").astype(float)
        )
        data_cleaned["living_space"] = data_cleaned["living_space"].astype(float)
        data_cleaned["floor_space"] = data_cleaned["floor_space"].str.extract(
            "(\d+,?\d*)"
        )
        data_cleaned["floor_space"] = (
            data_cleaned["floor_space"].str.replace(",", "").astype(float)
        )
        data_cleaned["floor"] = (
            data_cleaned["floor"].apply(self._parse_floor).astype(float)
        )
        data_cleaned["availability"] = data_cleaned["availability"]

        # Merge DataFrames
        cols_to_join = [
            "type_unified",
            "features",
            "Last refurbishment:",
            "Year built:",
        ]
        data_cleaned = data_cleaned.join(data[cols_to_join])
        data_cleaned.rename(
            columns={
                "type_unified": "type",
                "Last refurbishment:": "last_refurbishment",
                "Year built:": "year_built",
            },
            inplace=True,
        )
        data_cleaned.drop(
            ["municipality_address_s", "zip_address_s"], axis=1, inplace=True
        )

        # Set index for kaggle data
        if kaggle:
            data_cleaned["Index"] = data.iloc[:, 1]

        if return_gde:
            return data_cleaned.join(data.loc[:, "ForestDensityL":"gde_workers_total"])
        else:
            return data_cleaned
