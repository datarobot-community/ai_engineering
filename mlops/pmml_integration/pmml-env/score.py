import os
from functools import partial
from pypmml import Model

import custom

CUSTOM_PMML_MODEL = ".xml"

REGRESSION_PRED_COLUMN = "Predictions"


def load_serialized_model():
    """
    Load the serialized model from it's artifact.

    Returns
    -------
    Any
        The deserialized model

    Raises
    ------
    FileNotFoundError if a file could not be found in the working directory
        whose name starts with `custom_model.`
    """
    serialized_model_file = None

    for filename in os.listdir("."):
        path = os.path.join(".", filename)
        if os.path.isdir(path):
            continue
        if filename.endswith(CUSTOM_PMML_MODEL):
            if serialized_model_file:
                raise ValueError(
                    "Multiple serialized model files found. Remove extra artifacts."
                )
            serialized_model_file = path

    if not serialized_model_file:
        raise FileNotFoundError(
            "Could not find serialized model file. Serialized model file name "
            "should have an extension {}".format(CUSTOM_PMML_MODEL)
        )

    model = Model.load(serialized_model_file)
    return model


def outer_predict(data, model=None, positive_class_label=None, negative_class_label=None, **kwargs):
    """
    Makes predictions against the model using the custom predict
    method and returns a pandas DataFrame

    If the model is a regression model, the DataFrame will have a single column "Predictions"
    If the model is a classification model, the DataFrame will have a column for each class label
        with their respective probabilities

    Parameters
    ----------
    data: pd.DataFrame
        Data to make predictions against
    model: Any
        The model
    positive_class_label: str or None
        The positive class label if this is a binary classification prediction request
    negative_class_label: str or None
        The negative class label if this is a binary classification prediction request
    kwargs

    Returns
    -------
    pd.DataFrame
    """
    model = model or load_serialized_model()

    return custom.predict(data, model, positive_class_label, negative_class_label, **kwargs)
