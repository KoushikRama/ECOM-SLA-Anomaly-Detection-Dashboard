from datetime import datetime
import pandas as pd
import numpy as np

from core.generate_test_data import generate_test_data
from config.loader import load_data_config
from services.api_client import call_api
from config.settings import FASTAPI_URL, SAGEMAKER_URL


def run_pipeline(hours, backend):

    config = load_data_config()

    df_test = generate_test_data(
        start_date=datetime(2025, 4, 1),
        hours=hours,
        config=config
    )

    payload = df_test.copy()
    payload["timestamp"] = payload["timestamp"].astype(str)

    urls = {
        "fastapi": FASTAPI_URL,
        "sagemaker": SAGEMAKER_URL
    }


    payload = payload.astype(object)
    payload = payload.replace({np.nan: None})
    data = call_api(payload.to_dict(orient="records"), backend, urls)

    results = pd.DataFrame(data)

    # merge ground truth
    results["timestamp"] = df_test["timestamp"]
    results["is_anomaly"] = df_test["is_anomaly"].values
    results["anomaly_type"] = df_test["anomaly_type"].values

    return results