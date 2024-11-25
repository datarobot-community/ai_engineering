import json
import importlib
import os
from traceback import format_exc

import pandas as pd
from flask import Flask, request
from werkzeug.exceptions import InternalServerError

from score import outer_predict, load_serialized_model, REGRESSION_PRED_COLUMN

app = Flask(__name__)


@app.errorhandler(InternalServerError)
def internal_server_error_handler(error):
    response = {
        "message": InternalServerError.description,
        "exception": repr(error),
        "traceback": format_exc(),
    }
    return json.dumps(response), 500


def get_custom_model_instance():
    module_name = os.environ.get("MODULE_NAME")
    class_name = os.environ.get("CLASS_NAME")
    custom_model_module = importlib.import_module(module_name)
    CustomModelClass = getattr(custom_model_module, class_name)
    return CustomModelClass()


custom_model = load_serialized_model()
url_prefix = os.environ.get("URL_PREFIX", "")


@app.route("{}/predict/".format(url_prefix), methods=["POST"])
def predict():
    payload = request.form
    X = pd.read_csv(request.files["X"])
    positive_class_label = payload.get("positiveClassLabel")
    negative_class_label = payload.get("negativeClassLabel")
    predictions = outer_predict(
        X,
        model=custom_model,
        positive_class_label=positive_class_label,
        negative_class_label=negative_class_label,
    )
    if positive_class_label is not None and negative_class_label is not None:
        predictions = predictions.to_dict(orient="records")
    else:
        predictions = list(predictions[REGRESSION_PRED_COLUMN])
    return json.dumps({"predictions": predictions})


@app.route("{}/".format(url_prefix))
def ping():
    """This route is used to ensure that server has started"""
    return "Server is up!\n"
