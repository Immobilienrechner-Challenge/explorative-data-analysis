import pandas as pd
import numpy as np
import sweetviz as sv


def generate_sweetviz_report():

    df = pd.read_csv("../data/clean_gde_v2.csv")
    df_dirty = pd.read_csv("../data/immoscout_cleaned_lat_lon_fixed_v9.csv")

    sweet_report = sv.analyze(df)
    sweet_report.show_html("sweetviz-reports/sweetviz_report.html")

    sweet_report = sv.analyze(df_dirty)
    sweet_report.show_html("sweetviz-reports/sweetviz_report_uncleaned.html")

    cols = [
        "ForestDensityL",
        "ForestDensityM",
        "ForestDensityS",
        "NoisePollutionRailwayL",
        "NoisePollutionRailwayM",
        "NoisePollutionRailwayS",
        "NoisePollutionRoadL",
        "NoisePollutionRoadM",
        "NoisePollutionRoadS",
        "PopulationDensityL",
        "PopulationDensityM",
        "PopulationDensityS",
        "RiversAndLakesL",
        "RiversAndLakesM",
        "RiversAndLakesS",
        "WorkplaceDensityL",
        "WorkplaceDensityM",
        "WorkplaceDensityS",
        "distanceToTrainStation",
        "zip_code",
    ]
    sweet_report = sv.analyze(df.loc[:, cols])
    sweet_report.show_html("sweetviz-reports/sweetviz_SML.html")

    sweet_report = sv.analyze(
        df.loc[:, "gde_area_agriculture_percentage":"gde_workers_total"]
    )
    sweet_report.show_html("sweetviz-reports/sweetviz_gde.html")

    cols = [
        "municipality",
        "street",
        "street_nr",
        "zip_code",
        "canton",
        "Latitude",
        "Longitude",
    ]
    sweet_report = sv.analyze(df.loc[:, cols])
    sweet_report.show_html("sweetviz-reports/sweetviz_locality.html")

    cols = ["living_space", "rooms", "plot_area", "floor_space", "floor", "type"]
    sweet_report = sv.analyze(df.loc[:, cols])
    sweet_report.show_html("sweetviz-reports/sweetviz_immo.html")
