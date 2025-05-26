# -*- coding: utf-8 -*-
"""
%  nnUnet segmentation of the LV, with Endo and Epi segmentation and depth mask  
%  
% SYNTAX:  [P_Endo,P_Epi,LV_mask_slc]= ROI_NNUNET_KM(Dcm,Res,Folter_tmp)
%  
%
% INPUTS:   Dcm - Image matrix
%                 [y x slices]
%
%           Res - Pixel Resolution in mm
%                 [y x] default (2x2)
%
%           Folter_tmp - Temporaty folder to perform the segmentation
%                   default C:\Temp
%        
% OUTPUTS:  P_Endo - List of Coordinates of the Endocardium ROI
%                 [200pts [y x]]
%
%           P_Epi - List of Coordinates of the Epicardium ROI
%                 [200pts [y x]]
%
%           LV_Mask - Mask matrix 
%                 [y x slices]
%
%           Mask_Depth - Mask of depth based on the Epi/Endo countour 
%                 [y x slices]
%
% EXAMPLE:
%           [P_Endo,P_Epi,LV_Mask,Mask_Depth]= ROI_NNUNET_KM(Image,[2.3 2.3],'c:/temp');
%
%
% Kevin Moulin 05.24.2025
% Kevin.Moulin.26@gmail.com
%
% Ennis Lab @ UCLA: http://mrrl.ucla.edu
% Ennis Lab @ Stanford: https://med.stanford.edu/cmrgroup/software.html
% CREATIS Lab @ https://www.creatis.insa-lyon.fr/site/en
% Boston Children's Hospital @ https://research.childrenshospital.org/researchers/kevin-moulin
"""
import numpy as np
import os 
import sys
import json
import cv2
import scipy 
from scipy.interpolate import griddata
from matplotlib import pyplot as plt


def ROI_NNUNET_KM(Dcm, Res=[2, 2],Folder_tmp="C:\\Temp"):
    
    Dim=Dcm.shape;
    
    LV_Mask=np.zeros_like(Dcm)
    P_Endo=np.zeros((200,2,Dim[2]))
    P_Epi=np.zeros((200,2,Dim[2]))
    
    # Create meshgrid for interpolation
    Xq, Yq = np.meshgrid(np.arange(1, Dcm.shape[1] + 1), 
                         np.arange(1, Dcm.shape[0] + 1))
    
    # Initialize mask if it doesn't exist
    if 'Mask_Depth' not in locals():
        Mask_Depth = np.zeros((Dim[0], Dim[1], Dim[2]))
        
   
    #  set path to the Python executable
    pyRoot = 'C:\\Users\\CH240726\\AppData\\Local\\anaconda3';
    sys.path.append(pyRoot)
    sys.path.append( os.path.join(pyRoot, 'Library', 'mingw-w64', 'bin'))
    sys.path.append(   os.path.join(pyRoot, 'Library', 'usr', 'bin'))
    sys.path.append(   os.path.join(pyRoot, 'Library', 'bin'))
    sys.path.append(   os.path.join(pyRoot, 'Scripts'))
    sys.path.append(    os.path.join(pyRoot, 'bin'))

    # set Path to the nnUnet folders
    os.environ["nnUNet_results"] = "D:\\nnUnet\\Results"
    #os.environ["nnUNet_preprocessed"] = "D:\\nnUnet\\PrePro" # not needed here
    #os.environ["nnUNet_raw"] = "D:\\nnUnet\\RAW" # not needed here
    #os.environ["nnUNet_results"],'D:\\nnUnet\\Results')

    # For each slice, we call the segmentation. 
    for cpt_slc in range(Dim[2]):
        try:
           epicardium, endocardium, LV_tmp = nnUnet_local(Dcm[:,:,cpt_slc],Res,Folder_tmp);
           LV_Mask[:,:,cpt_slc]=LV_tmp;
           P_Endo[:,:,cpt_slc]=endocardium;
           P_Epi[:,:,cpt_slc]=epicardium;
           
           # We have the Endo/Epi boundaries, now let's calculate a depth
           # mask.
           # Create value arrays for boundaries
           Endo_Line = np.zeros((endocardium.shape[0],))  # 0 for endocardium
           Epi_Line = np.ones((epicardium.shape[0],))     # 1 for epicardium
           
           # Concatenate boundary coordinates and values
           PosRoi = np.vstack([epicardium, endocardium])
           LineRoi = np.concatenate([Epi_Line, Endo_Line])
           
           # Interpolate to create depth mask
           Mask_Depth[:, :, cpt_slc] = griddata(
               points=PosRoi,           # Known boundary points
               values=LineRoi,          # Corresponding depth values
               xi=(Xq, Yq),            # Query points (entire image grid)
               method='linear',         # Linear interpolation
               fill_value=np.nan       # Fill value for points outside convex hull
           )
           
        except Exception as e:
            raise e
            print("Error Running NNUNET slice "+cpt_slc)
            
    return P_Epi, P_Endo, LV_Mask, Mask_Depth
def nnUnet_local(Dcm, res,rdir):
    
      epicardium=[];
      endocardium=[];
      folderIn=os.path.join(rdir, 'tmpIn');
      folderOut=os.path.join(rdir, 'tmpOut') 
      fileIn='tmp_0000_0000';
      fileOut='tmp_0000.png';
      if not os.path.exists(folderIn):
          os.mkdir(folderIn)
      if not os.path.exists(folderOut):
          os.mkdir(folderOut)
  
     # if the json file exist, delete it
      if os.path.exists(os.path.join(folderIn, fileIn+'.json') ):
          
          os.remove(os.path.join(folderIn, fileIn+'.json') )
      with open(os.path.join(folderIn, fileIn+'.json') , 'w', encoding='utf-8') as f:
          json.dump(str(res), f, ensure_ascii=False, indent=4)
     
      # write the pixel resolution to a json file
      if os.path.exists(os.path.join(folderIn, fileIn+'.png') ):
          # delete the file
          os.remove(os.path.join(folderIn, fileIn+'.png') )  
      imgIn=(255*(Dcm/np.max(Dcm[:]))).astype(np.uint8);
      cv2.imwrite(os.path.join(folderIn, fileIn+'.png'), imgIn) # Save the image
      
      # Call the nnUnet Command
      NNUNET_command='nnUNetv2_predict -i "'+folderIn+'" -o "'+folderOut+'" -c 2d -d 7 -f all -p nnUNetPlans -device cpu';
      os.system(NNUNET_command);
      LV_tmp=cv2.imread(os.path.join(folderOut, fileOut))
      img = cv2.cvtColor(LV_tmp*150, cv2.COLOR_BGR2GRAY)
      LV_tmp2=np.max(LV_tmp,axis=2);
      
      # We have the LV mask, now let's find the Endo/Epi boudaries
      contours, hier = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

      Bound1=contours[1].squeeze()
      Bound0=contours[0].squeeze()
      
      Dim1=Bound1.shape;
      Dim0=Bound0.shape;
      
      Bary=np.mean(Bound0,0)
      Dist0=np.max(np.sqrt(np.sum((Bound0-Bary)**2,axis=1)));
      Dist1=np.max(np.sqrt(np.sum((Bound1-Bary)**2,axis=1))); 
      
      # Interpolate the boudaries to 200 points
      linit= np.arange(0,Dim0[0]+1,1)
      linit1= np.arange(0,Dim1[0]+1,1)
      lspace = np.linspace(0, Dim0[0], 200)
      lspace1 = np.linspace(0, Dim1[0], 200)
      iBound0=np.zeros((200,2));
      iBound1=np.zeros((200,2));
      
      f_linear = scipy.interpolate.interp1d(linit,np.hstack((Bound0[:,0], Bound0[0,0]))) 
      iBound0[:,0] = f_linear(lspace) 

      f_linear = scipy.interpolate.interp1d(linit,np.hstack((Bound0[:,1], Bound0[0,1]))) 
      iBound0[:,1] = f_linear(lspace) 

      f_linear = scipy.interpolate.interp1d(linit1,np.hstack((Bound1[:,0], Bound1[0,0]))) 
      iBound1[:,0] = f_linear(lspace1) 

      f_linear = scipy.interpolate.interp1d(linit1,np.hstack((Bound1[:,1], Bound1[0,1]))) 
      iBound1[:,1] = f_linear(lspace1) 

   
      epicardium=iBound0;
      endocardium=iBound1;
      if Dist0>Dist1:
          epicardium=iBound0;
          endocardium=iBound1;
      # colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

      # # Draw all contours, and their children, with different colors
      # out = cv2.cvtColor(imgIn, cv2.COLOR_GRAY2BGR)
     
      # cv2.drawContours(out, epicardium, -1, colors[0], 2)
      # cv2.drawContours(out, endocardium, -1, colors[1], 2)
      # cv2.imshow('out', out)
      return epicardium, endocardium, LV_tmp2 