from chemprop.args import PredictArgs
import pandas as pds


def load_model():
    """
    Modify this method to deserialize you model if this environment's standard model
    loader cannot.  For example, if your custom model archive contains multiple pickle
    files, you must explicitly load which ever one corresponds to your serialized model
    here.

    Returns
    -------
    object, the deserialized model
    """
    return "None"


def predict(data, model_predict):
    """
    Modify this method to add pre and post processing for scoring calls.  For example, this can be
    used to implement one-hot encoding for models that don't include it on their own.

    Parameters
    ----------
    data: pd.DataFrame
    model_predict: Callable[[pd.DataFrame], pd.DataFrame]

    Returns
    -------
    pd.DataFrame
    """
    # Execute any steps you need to do before scoring

    # This method makes predictions against the raw, deserialized model
    #predictions = model_predict(data)

    data.to_csv("/opt/code/chemprop_folder/for_scoring.csv", index=False)

    args = PredictArgs().parse_args([
        '--test_path', '/opt/chemprop_folder/for_scoring.csv',
        '--checkpoint_path', '/opt/code/model.pth',
        '--preds_path', '/opt/chemprop_folder/preds.csv'
    ])

    make_predictions(args)

    preds_df = pds.read_csv("/opt/chemprop_folder/preds.csv")
    sh = str(preds_df.shape)
    print(sh)

    preds_df = preds_df.rename(columns = {"p_np": "positive_class_label"})
    preds_df = preds_df.drop(columns=['smiles'])
    preds_df["negative_class_label"] = 1 - preds_df["positive_class_label"]

    print(preds_df.head())

    # Execute any steps you need to do after scoring
    # Note: To properly send predictions back to DataRobot, the returned DataFrame should contain a
    # column for each output label for classification or a single value column for regression
    return preds_df
