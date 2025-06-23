!pip install -q condacolab
import condacolab
condacolab.install()

#!conda install -c bioconda fragpipe

# Create a conda environment and export it
!conda create -n fragpipe_env -c bioconda fragpipe -y
!conda activate fragpipe_env
!conda env export > /content/drive/MyDrive/fragpipe_environment.yml

# In future sessions, recreate from the exported file:
!conda env create -f /content/drive/MyDrive/fragpipe_environment.yml
!conda activate fragpipe_env




!pip install pyteomics lxml

!pip install git+https://github.com/gtluu/timsconvert



#Install alphatims
!pip install git+https://github.com/MannLabs/alphatims.git
