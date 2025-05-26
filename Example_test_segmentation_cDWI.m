load('cDWI_example.mat')

% Run the segmentation on the nDWI images
[P_Endo_0,P_Epi_0,LV_Mask_0,Mask_Depth_0]= ROI_NNUNET_KM(Trace(:,:,:,1),[2 2],'C:\Temp');

% Run the segmentation on the DWI images
[P_Endo_1,P_Epi_1,LV_Mask_1,Mask_Depth_1]= ROI_NNUNET_KM(Trace(:,:,:,2),[2 2],'C:\Temp');

%%
% Show an overlay of both segmentations for the mid slice
figure
imagesc(LV_Mask_0(:,:,2)+LV_Mask_1(:,:,2)),colormap('hot')
hold on
%Endo in Red
plot(P_Endo_0(:,1,2),P_Endo_0(:,2,2),'r-')
plot(P_Endo_1(:,1,2),P_Endo_1(:,2,2),'r--')

%Epi in blue
plot(P_Epi_0(:,1,2),P_Epi_0(:,2,2),'b-')
plot(P_Epi_1(:,1,2),P_Epi_1(:,2,2),'b--')