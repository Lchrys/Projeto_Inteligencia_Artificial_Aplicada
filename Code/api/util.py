"""Serialização de DataFrames para JSON da API."""

import json

import pandas as pd


def registros(quadro: pd.DataFrame) -> list:
    if quadro.empty:
        return []
    return json.loads(quadro.to_json(orient="records"))
