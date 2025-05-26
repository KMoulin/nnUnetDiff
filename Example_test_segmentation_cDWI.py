# -*- coding: utf-8 -*-
"""
Created on Mon May 26 18:22:37 2025

@author: kevin
"""

from matplotlib import pyplot as plt
from ROI_NNUNET_KM import ROI_NNUNET_KM
import scipy.io

Trace=scipy.io.loadmat('cDWI_example.mat').get("Trace")

# Run the segmentation on the nDWI images
P_Epi_0, P_Endo_0, LV_Mask_0, Mask_Depth_0=ROI_NNUNET_KM(Trace[:,:,:,0], [2, 2],"C:\\Temp")

# Run the segmentation on the DWI images
P_Epi_1, P_Endo_1, LV_Mask_1, Mask_Depth_1=ROI_NNUNET_KM(Trace[:,:,:,1], [2, 2],"C:\\Temp")
#%%

# Show an overlay of both segmentations for the mid slice
plt.imshow(LV_Mask_0[:,:,1]+LV_Mask_1[:,:,1], cmap='hot')
# Endo in Red
plt.plot(P_Endo_0[:,0,1],P_Endo_0[:,1,1], color='red', linestyle='-')
plt.plot(P_Endo_1[:,0,1],P_Endo_1[:,1,1], color='red', linestyle='--')

# Epi in Blue
plt.plot(P_Epi_0[:,0,1],P_Epi_0[:,1,1], color='blue', linestyle='-')
plt.plot(P_Epi_1[:,0,1],P_Epi_1[:,1,1], color='blue', linestyle='--')

plt.show()