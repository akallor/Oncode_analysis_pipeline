#Download and save the data to Drive
!wget ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2023/11/PXD038782/230717_NHG_malignant_CLL_12_W632_Rep1.d.tar -O /content/drive/MyDrive/Utrecht_Oncode_pipeline/230717_NHG_malignant_CLL_12_W632_Rep1.d.tar
!wget ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2023/11/PXD038782/230717_NHG_malignant_CLL_12_W632_Rep2.d.tar -O /content/drive/MyDrive/Utrecht_Oncode_pipeline/230717_NHG_malignant_CLL_12_W632_Rep2.d.tar
!wget ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2023/11/PXD038782/230717_NHG_malignant_CLL_12_W632_Rep3.d.tar -O /content/drive/MyDrive/Utrecht_Oncode_pipeline/230717_NHG_malignant_CLL_12_W632_Rep3.d.tar

!for f in /content/drive/MyDrive/Utrecht_Oncode_pipeline/*.tar; do tar -xf "$f" -C /content/drive/MyDrive/Utrecht_Oncode_pipeline/; done
