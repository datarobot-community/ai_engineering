import pandas as pd

# for test we can use fake model_id and project_id, since we are not going to make real api calls
MODEL_ID1 = '5b2b44639c5b179c69bd3799'
MODEL_ID2 = 'FFFF44639c5b179c69bdFFFF'
PROJECT_ID1 = '5b2b4281ff83430f31457be0'
PROJECT_ID2 = 'FFFF4281ff83430f3145FFFF'
# Incoming data can't use this feature/column names(They are used in pipeline)
RESERVED_COLUMNS = ('project_id', 'model_id', 'premium', 'predicted_price')


def data_prepare(features_df):
    """This function runs before sending data to scoring.
    Here input data can be modified, prediction model can be different for each line.

    :param features_df: features from SOAP request as Pandas DataFrame + 'premium' column
    :return: DataFrame for scoring with columns 'project_id' and 'model_id'
    """

    # we need project_id:model_id combination for scoring
    projects_models = [
        {'project_id': PROJECT_ID1,
         'model_id': MODEL_ID1},
        {'project_id': PROJECT_ID2,
         'model_id': MODEL_ID2},
    ]
    projects_models_df = pd.DataFrame(projects_models)

    # add to each data row 'project_id' and 'model_id'  for each used model
    # so in this example, each row will be scored twice(once by each model)
    projects_models_df['key'] = 0
    features_df['key'] = 0
    result_df = features_df.merge(projects_models_df, how='outer')
    del result_df['key']

    return result_df


def business_logic(scored_df):
    price_adjustment = scored_df['predicted_price'].mean() / scored_df['predicted_price'].max()
    return (price_adjustment, scored_df)


# This code is executed only when the business logic is saved as a standalone
# Python file and executed by calling `python demo_code.py`.
# It is a way to test business logic outside the price adjustment solution.
if __name__ == '__main__':
    test_data = [
        {'column1': 'c1_data1',
         'column2': 'c2_data1'},
        {'column1': 'c1_data2',
         'column2': 'c2_data2'},
        {'column1': 'c1_data3',
         'column2': 'c2_data3'},
    ]

    input_df = pd.DataFrame(test_data)

    res = data_prepare(input_df)
    res['predicted_price'] = 3
    res['premium'] = 4
    print(res)
    print(business_logic(res))
