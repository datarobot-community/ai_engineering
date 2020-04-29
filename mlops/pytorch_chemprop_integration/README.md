<b>BLUF:</b>
- Chemprop library contains message passing neural networks for molecular property prediction and is used by the pharmaceutical companies.
- Currently we use only CPU for training. Activation of GPU in Pytorch may require additional setup.
- Ready for drop in env and models' tar files are in this repo.
- Each model tar file contains the trained model and the corresponding custom.py file.


<b>Steps to integrate Chemprop library (molecular property prediction) into DataRobot dropin Pytorch environment:</b>

- Create empty folder on your local machine (let's name it python3_pytorch_chemprop)

- Copy the following folder and files to the created folder:<br>
  server<br>
  score.py<br>
  custom.py<br>
  start_server.sh<br>

- Clone Chemprop library (https://github.com/chemprop/chemprop)

- Copy the content of the cloned repo to the python3_pytorch_chemprop

- Delete data.tar.gz and splits.tar.gz from python3_pytorch_chemprop. These files contain different datasets and their splits. We don't need them in production environment but you can use them to play with Chemprop locally.

- Delete .git and .gitignore folders (their size exceeds 150Mb so we simply try to have our env lightweight).
<b>IMPORTANT:</b> once these folders are deleted you can't use Chemprop library for training.
The reason is that Chemprop uses internally typed-argument-parser library and it checks the reproducibility information.
Not to have the possibility to train is not critical right now. Once we have the fit() function available for custom models we can revisit this step.

- Create the Dockerfile (includes Ubuntu, Anaconda and Nvidia CUDA)

- Create tar file with your environment<br>
<code>tar -czvf pytorch-chemprop-env.tar.gz python3_pytorch_chemprop/</code>

- (Optional) Train your model using Chemprop inside your local docker container (bbbp.csv and lipo.csv used below can be found in data.tar.gz from Chemprop repo)<br>
<code>docker build -t pytorch-chemprop:1.0 .</code><br><br>
<code>docker run --name pytorch-chemprop -it pytorch-chemprop:1.0 sh</code><br><br>
<code>python train.py --data_path /opt/chemprop_folder/bbbp.csv --dataset_type classification --save_dir /opt/chemprop_folder</code><br><br>
<code>python train.py --data_path /opt/chemprop_folder/lipo.csv --dataset_type regression --save_dir /opt/chemprop_folder</code><br>

- (Optional) Predict with your model inside your local docker container<br>
<code>python predict.py --test_path /opt/chemprop_folder/for_prediction_100.csv --checkpoint_path /opt/chemprop_folder/fold_0/model_0/model.pt --preds_path /opt/chemprop_folder/bbbp_preds.csv</code><br><br>
<code>python predict.py --test_path /opt/chemprop_folder/lipo_for_predictions.csv --checkpoint_path /opt/chemprop_folder/fold_0/model_0/model.pt --preds_path /opt/chemprop_folder/lipo_preds.csv</code><br>

- (Optional) Copy the trained model from your local docker container to your local machine<br>
<code>docker cp pytorch-chemprop:/opt/code/model.pt classification_model/model.pt</code>

- Create empty folder for models (one for regression and one for binary classification) on your local machine

- Copy custom.py from python3_pytorch_chemprop folder to the each of the model folders

- Modify custom.py for regression model (example is in this repo)

- Modify custom.py for binary classification model (example is in this repo)

- Create tar files with your model<br>
<code>tar -czvf regression-model.tar.gz regression_model/</code><br>
<code>tar -czvf classification-model.tar.gz classification_model/</code><br>

- Follow the MLOps procedures for custom env/model creation and deployment
