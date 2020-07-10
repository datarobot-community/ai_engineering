import importlib.util
import os

TMP_FILE = 'tmp.py'
SRC_FILE = f'/tmp/datarobotapiwrapper/{TMP_FILE}'


def save_module(src):
    if not os.path.exists(os.path.dirname(SRC_FILE)):
        os.makedirs(os.path.dirname(SRC_FILE))
    with open(SRC_FILE, 'w') as f:
        f.writelines(src)


def get_function(fun_name='get_result'):
    module_spec = importlib.util.spec_from_file_location(
        'tmp_src', SRC_FILE)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    fun = getattr(module, fun_name)
    return fun


def call_user_function(src, fun_name, dataframe):
    save_module(src)
    #print('call_user_function', fun_name)
    fun = get_function(fun_name)
    #print('call_user_function', fun_name)
    #print(len(dataframe.index))
    result = fun(dataframe)
    #print(result)
    return result
