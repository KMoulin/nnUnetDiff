# nnUnetDiff

## Installation 
- Install Python 3.12+
- Install Pytorch with CUDA or with CPU
      https://pytorch.org/get-started/locally/
  
- Install nnunet v2 :
      pip install nnunetv2

# Running nnUnet in Python and in Matlab

The nnUnet approach use 3 folders for training, testing and running. These folder path should be added as environement variable as described here:
https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/set_environment_variables.md

If you are only planning on using the network for making prediction/segmentation, you need only the PrePro folder and the Result folder added to your environement variables.
For simplicity, these two environement variable are added to the path before within the ROI_nnUnet Matlab and Python code.


In Matlab the path to the Python executable is needed to call Python and run nnUnet. In the example Matlab code, the Python directory is coded. 


The main command to call the nnUnet is as follow:
NNUNET_command=['nnUNetv2_predict -i "' folderIn '" -o "' folderOut '" -c 2d -d 7 -f all -p nnUNetPlans -device cpu'];
system(NNUNET_command);

folderIn is a temporary folder where the dicom image is converted to jpeg
folderOut is a temporary folder where the network will copy in prediciton in a jpeg format
- -c 2d indicates we are doing a 2D prediciton
- -d is the ID number of the trained network, in this repository the diffusion segmentation network has the ID 7. 
- -f all indicates we are using the network trained with all fold. 
- -p nnUnetPlans is the type of network
- -device cpu indicates the network will use the cpu only for prediction. If you have CUDA install you may use the gpu for faster prediction. 


