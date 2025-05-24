# nnUnetDiff

Trained network for the automatic LV segmentation of cardiac diffusion image. Input of the network is a simple DWI or nDWI image, the ouput is a mask/segmentation of the LV
This package countain the trained weights of the nnUnet and a matlab and a python code to run the network as well as a set of dataset example.  

This has been tested only on a Windows 10 & 11 system. 

## Installation 
- Install Python 3.12+
- Install Pytorch with CUDA or with CPU
  - https://pytorch.org/get-started/locally/
- Install nnUnet v2 :
  - pip install nnunetv2

# Running nnUnet

The nnUnet approach use 3 folders for training, testing and running. These folder path should be added as environement variable as described here:
https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/set_environment_variables.md

If you are only planning on using the network for making prediction/segmentation, you need only the PrePro folder and the Result folder added to your environement variables.
For simplicity, these two environement variable are added to the path before within the ROI_nnUnet Matlab and Python example codes.
Some Python path are also needed to run nnUnet wich are also added in the example codes.

The main system command to call the nnUnet is as follow:
nnUNetv2_predict -i "' folderIn '" -o "' folderOut '" -c 2d -d 7 -f all -p nnUNetPlans -device cpu

- _folderIn_ is a temporary folder where the dicom image is converted to jpeg
- _folderOut_ is a temporary folder where the network will copy in prediciton in a jpeg format
- _-c 2d_ indicates we are doing a 2D prediciton
- _-d 7_ is the ID number of the trained network, in this repository the diffusion segmentation network has the ID 7. 
- _-f all_ indicates we are using the network trained with all fold. 
- _-p nnUnetPlans_ is the type of network
- _-device cpu_ indicates the network will use the cpu only for prediction. If you have CUDA install you may use the gpu for faster prediction. 

# Matlab Example 


