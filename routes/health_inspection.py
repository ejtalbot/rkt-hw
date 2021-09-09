"""Module for making health inspection predictions"""
import pickle
from datetime import datetime

from utils.data_validation import get_sanitized_data
from utils.mappings import BOROUGH_NAME_TO_INT_MAP


def create_prediction(restaurants):
    """Route to make restaurant grade predictions by passing inputs
    through a RandomForestClassifier model

    Args:
        restaurants: Dictionary of restaurants with the following format:
            {
                "0": {
                    "borough": "Manhattan",
                    "tstamp": "2021-05-15",
                    "cuisine": "Pizza"
                },
                "1": {
                    "borough": "Queens",
                    "tstamp": "2021-06-15",
                    "cuisine": "Asian"
                }
            }

    Returns:
        Web response json with the restaurant id mapped to the
        probability it recieves an A

    """
    with open("model.pkl", "rb") as handle:
        model_reloaded = pickle.load(handle)

    sample_data_df = get_sanitized_data("samples")

    model_inputs = [
        [
            BOROUGH_NAME_TO_INT_MAP[restaurant["borough"]],
            sample_data_df["cuisine"].value_counts()[restaurant["cuisine"]],
            datetime.strptime(restaurant["tstamp"], "%Y-%m-%d").weekday() + 1,
        ]
        for restaurant in restaurants.values()
    ]

    model_probability_output = model_reloaded.predict_proba(model_inputs)[:, 1]

    prediction_model_response = {
        str(id): round(probability, 2)
        for id, probability in enumerate(model_probability_output)
    }

    return prediction_model_response
