function [P_Endo,P_Epi,LV_Mask,Mask_Depth]= ROI_NNUNET_KM(Dcm,Res,Folder_tmp)
%  nnUnet segmentation of the LV, with Endo and Epi segmentation and depth mask  
%  
% SYNTAX:  [P_Endo,P_Epi,LV_mask_slc]= ROI_NNUNET_KM(Dcm,)
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


    if nargin < 2
        Res=[2 2];
    end
    if nargin < 3
        Folder_tmp='C:\Temp';
    end
    
    
    P_Endo=[];
    P_Epi=[];
    LV_Mask=[];
    Mask_Depth=[];
    
    [Xq,Yq] = meshgrid(1:size(Dcm,2),1:size(Dcm,1));
    
    disp('nnUnet ROI') 

    % set path to the Python executable
    pyExec = 'C:\Users\kevin\anaconda3\python.exe';  % Path      
    pyRoot = fileparts(pyExec);
    p = getenv('PATH');
    p = strsplit(p, ';');
    addToPath = {
        pyRoot
        fullfile(pyRoot, 'Library', 'mingw-w64', 'bin')
        fullfile(pyRoot, 'Library', 'usr', 'bin')
        fullfile(pyRoot, 'Library', 'bin')
        fullfile(pyRoot, 'Scripts')
        fullfile(pyRoot, 'bin')
        };
    p = [addToPath(:); p(:)];
    p = unique(p, 'stable');
    p = strjoin(p, ';');
    setenv('PATH', p);
    
    % set Path to the nnUnet folders
    setenv('nnUNet_results','C:\Users\kevin\Downloads\nnUnet\Models\Results')
    % setenv('nnUNet_preprocessed','') % not needed here
    % setenv('nnUNet_raw','') % not needed here
     
    % For each slice, we call the segmentation. 
    for cpt_slc=1:1:size(Dcm,3)
        try
           [epicardium, endocardium, LV_tmp] = nnUnet_local(Dcm(:,:,cpt_slc),Res,Folder_tmp); %enum.recon_dir
           LV_Mask(:,:,cpt_slc)=LV_tmp;
           P_Endo(:,:,cpt_slc)=endocardium;
           P_Epi(:,:,cpt_slc)=epicardium;
           
           % We have the Endo/Epi boundaries, now let's calculate a depth
           % mask.
           Endo_Line = zeros(size(endocardium));
           Epi_Line = ones(size(epicardium));
           PosRoi = cat(1,epicardium,endocardium);
           LineRoi   = cat(1,Epi_Line,Endo_Line);
           Mask_Depth(:,:,cpt_slc) = griddata(PosRoi(:,1),PosRoi(:,2),LineRoi(:,1),Xq,Yq);
        catch
             LV_Mask(:,:,cpt_slc)=nan(size(Dcm,1),size(Dcm,2));
             P_Endo(:,:,cpt_slc)=nan(200,2);
             P_Epi(:,:,cpt_slc)=nan(200,2);
             Mask_Depth(:,:,cpt_slc)=nan(size(Dcm,1),size(Dcm,2));
             disp(['Error Running NNUNET slice ' num2str(cpt_slc)]);
        end
    
    end
    
    
    function [epicardium, endocardium, LV_tmp]= nnUnet_local(Dcm,res,rdir)
    
        epicardium=[];
        endocardium=[];
    
        % Set some variable
        folderIn=[rdir '\tmpIn'] ;
        folderOut=[rdir '\tmpOut'] ;
        fileIn='tmp_0000_0000';
        fileOut='tmp_0000.png';
        mkdir(folderIn) % create the folderIn
        mkdir(folderOut) % create the folderOut
        jsonStr = jsonencode(res); % write the pixel resolution to a json file
        
        % Write the normalized input image to the temp folder
        imwrite(Dcm./max(Dcm(:)),[folderIn '/' fileIn '.png']);
        file = fopen([folderIn '/' fileIn '.json'],'w');
        fwrite(file, jsonStr);
        fclose(file);
    
        % Call the nnUnet Command
        NNUNET_command=['nnUNetv2_predict -i "' folderIn '" -o "' folderOut '" -c 2d -d 7 -f all -p nnUNetPlans -device cpu'];
        system(NNUNET_command);
        LV_tmp=imread([folderOut '\' fileOut]);
    
        % We have the LV mask, now let's find the Endo/Epi boudaries
        [B,L] = bwboundaries(LV_tmp);
        if length(B)~=2
            error('LV Boundaries not detected');
        end
        
        % Inperpolate the boundary to 200 points
        for k = 1:length(B)
           boundary = B{k};
    
           xq=linspace(1,size( boundary,1),200);
           yq=linspace(1,size(boundary,1),200);
           bound(:,1,k) = interp1(boundary(:,1),xq);
           bound(:,2,k) = interp1(boundary(:,2),yq);
    
        end
        [~,Idx]=sort(squeeze(max(bound(:,1,:))-min(bound(:,1,:)))); % sort them from small to big
        endocardium=squeeze(bound(:,2:-1:1,Idx(1)));
        if length(Idx)>1
            epicardium=squeeze(bound(:,2:-1:1,Idx(2)));
        else
            epicardium=endocardium;
        end
    end
end