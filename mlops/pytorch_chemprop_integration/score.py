import os
import pickle
from functools import partial

import custom
import pandas as pd
import torch
import torch.nn as nn
from torch.autograd import Variable

CUSTOM_MODEL_TORCH_EXTENSION = ".pth"

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
    model = custom.load_model()
    if model:
        return model
    for filename in os.listdir("."):
        path = os.path.join(".", filename)
        if os.path.isdir(path):
            continue
        if filename.endswith(CUSTOM_MODEL_TORCH_EXTENSION):
            if serialized_model_file:
                raise ValueError(
                    "Multiple serialized model files found. Remove extra artifacts "
                    "or overwrite custom.load_model"
                )
            serialized_model_file = path

    if not serialized_model_file:
        raise FileNotFoundError(
            "Could not find serialized model file. Serialized model file name "
            "should have an extension {}".format(CUSTOM_MODEL_TORCH_EXTENSION)
        )

    model = torch.load(serialized_model_file)
    model.eval()
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
    internal_predict = partial(
        _model_predict,
        model=model,
        positive_class_label=positive_class_label,
        negative_class_label=negative_class_label,
        **kwargs
    )
    return custom.predict(data, internal_predict)


def _model_predict(data, model, positive_class_label=None, negative_class_label=None, **kwargs):
    """
    Internal prediction method for pytorch,
    makes predictions against the model, and returns a pandas DataFrame

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
    data = Variable(torch.from_numpy(data.values).type(torch.FloatTensor))
    with torch.no_grad():
        predictions = model(data).cpu().data.numpy()
    if positive_class_label is not None and negative_class_label is not None:
        if predictions.shape[1] == 1:
            predictions = pd.DataFrame(predictions, columns=[positive_class_label])
            predictions[negative_class_label] = 1 - predictions[positive_class_label]
        else:
            predictions = pd.DataFrame(
                predictions, columns=[negative_class_label, positive_class_label]
            )
    else:
        predictions = pd.DataFrame(predictions, columns=[REGRESSION_PRED_COLUMN])

    return predictions
