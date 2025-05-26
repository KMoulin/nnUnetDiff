# nnUnetDiff

Trained network for the automatic LV segmentation of cardiac diffusion image. Input of the network is a simple DWI or nDWI image, the ouput is a mask/segmentation of the LV.
This package countain the trained weights of the nnUnet, a matlab and a python code to run the network as well as a set of dataset example.  

This has been tested only on Windows 10 & 11 systems. 

## Installation 
- Install Python 3.12+
- Install Pytorch with CUDA or with CPU
  - https://pytorch.org/get-started/locally/
- Install nnUnet v2 :
  - pip install nnunetv2

# Copying the model
Download the trained model from the Release: https://github.com/KMoulin/nnUnetDiff/releases/download/v1.0.0.0/Models.zip
Unzip the folder but make sure to keep the subfolder structure "\Results\Dataset007_All\nnUNetTrainer__nnUNetPlans__2d" which is recognized by nnUnet

# Running nnUnet

The nnUnet approach use 3 folders for training, testing and running. These folder path should be added as environement variable as described here:
https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/set_environment_variables.md

If you are only planning on using the network for making prediction/segmentation, you need only the Result containing the trainend model added to your environement variables.
For simplicity, these two environement variable are added to the path within the ROI_nnUnet Matlab and Python example codes. 
Some Python path are also needed to run nnUnet wich are also added in the example codes.

>[!IMPORTANT]
>Please adjust these path in the ROI_NNUNET_KM.m/.py for your system file before running them!
>Use the path where you copied the trained model!

The main system command to call the nnUnet is as follow:
nnUNetv2_predict -i "' folderIn '" -o "' folderOut '" -c 2d -d 7 -f all -p nnUNetPlans -device cpu

- _folderIn_ is a temporary folder where the dicom image is converted to jpeg
- _folderOut_ is a temporary folder where the network will copy in prediciton in a jpeg format
- _-c 2d_ indicates we are doing a 2D prediciton
- _-d 7_ is the ID number of the trained network, in this repository the diffusion segmentation network has the ID 7. 
- _-f all_ indicates we are using the network trained with all fold. 
- _-p nnUnetPlans_ is the type of network
- _-device cpu_ indicates the network will use the cpu only for prediction. If you have CUDA installed you may use the gpu for faster prediction. 

# Matlab 

The file "Example_test_segmentation_cDWI.m" show an example of segmentation for Matlab. The function calling segmentation routine is located in the file "ROI_NNUNET_KM.m" 
No external depencies are needed

# Python

The file "Example_test_segmentation_cDWI.py" show an example of segmentation for Matlab. The function calling segmentation routine is located in the file "ROI_NNUNET_KM.py"
The Open CV package is needed into the ROI_NNUNET_KM routine: pip install opencv-python
