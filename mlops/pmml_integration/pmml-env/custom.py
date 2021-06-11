
def predict(data, model, positive_class_label=None, negative_class_label=None, **kwargs):
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
    PROB_IRIS_SETOSA = "P_classIris_setosa"

    print(str(data.shape))
    print(data.head())

    result = model.predict(data)

    result = result[[PROB_IRIS_SETOSA]]
    result = result.rename(columns = {PROB_IRIS_SETOSA: positive_class_label})
    result[negative_class_label] = 1 - result[positive_class_label]

    print(str(result))

    # Execute any steps you need to do after scoring
    # Note: To properly send predictions back to DataRobot, the returned DataFrame should contain a
    # column for each output label for classification or a single value column for regression
    return result
