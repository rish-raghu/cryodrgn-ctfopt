# CryoDRGN-CtfOpt: Towards Coarse-to-Fine Optimization for 3D CryoEM Reconstruction

[CryoDRGN](http://cryodrgn.cs.princeton.edu) is a neural network based algorithm for heterogeneous cryo-EM reconstruction. In this project developed for the course COS526: Neural Rendering at Princeton, we attempt to integrate coarse-to-fine optimization strategies into CryoDRGN. The project report can be found [here](https://drive.google.com/file/d/1ZuU-i5hVv6woIx91LF9HWpSMExnAU0x5/view?usp=share_link).

## Installation/dependencies:

To install cryoDRGN, git clone the source code and install the following dependencies with anaconda:

    # Create conda environment
    conda create --name cryodrgn1 python=3.9
    conda activate cryodrgn1

    # Install dependencies
    conda install pytorch -c pytorch
    conda install pandas

    # Install dependencies for latent space visualization
    conda install seaborn scikit-learn
    conda install umap-learn jupyterlab ipywidgets cufflinks-py "nodejs>=15.12.0" -c conda-forge

    # Clone source code and install
    git clone https://github.com/zhonge/cryodrgn.git
    cd cryodrgn
    pip install .

## Data
Download the data from [Google Drive](https://drive.google.com/drive/folders/1TVN54VXFq3bTmR-ltGqDw3hf8LlJt6t1?usp=sharing). A subset of the scripts used for generation of the datasets is in the `data_gen` directory. 

## Homogenous Reconstruction with Pose Supervision
Run the `train_nn` command with ground truth poses in order to train a homogenous model and output a reconstruction after each epoch. We report results for three built-in positional encoding types, which can be set with the `pe-type` argument: _gaussian_, _geom_ft_, and _geom_lowf_. We use 10k images of the full dataset for the reported results, which can be specified with the `ind` parameter.
	
	$ cryodrgn train_nn data/homo/proj.snr0.1.mrcs --poses data/homo/poses.pkl --ctf data/homo/ctf.pkl --uninvert-data --pe-type gaussian --ind data/homo/10000.pkl -o recon

[Residual MFN](https://shekshaa.github.io/ResidualMFN/) can be trained in place of the positional encoding by supplying _rmfn_ to the `pe-type` argument as well.
	
	$ cryodrgn train_nn data/homo/proj.snr0.1.mrcs --poses data/homo/poses.pkl --ctf data/homo/ctf.pkl --uninvert-data --pe-type rmfn --ind data/homo/10000.pkl -o recon

[BARF](https://chenhsuanlin.bitbucket.io/bundle-adjusting-NeRF/) can be applied to any of the positional encodings using a geometric series of frequencies (`pe-type` = _geom_lowf_, _geom_ft_, _geom_full_, _geom_nohighf_) by supplying the `barf-epochs` parameter. If we set `barf-epochs` to 10, for example, the BARF $\alpha$ parameter will linearly increase from 0 to `pe-dim` during the first 10 epochs of training, after which it is held constant at `pe-dim`.

	$ cryodrgn train_nn data/homo/proj.snr0.1.mrcs --poses data/homo/poses.pkl --ctf data/homo/ctf.pkl --uninvert-data --pe-type geom_lowf --barf-epochs 10 --ind data/homo/10000.pkl -o recon

To compute the FSC curves between the ground truth volume and the reconstructions at each epoch, and report the resolutions across training at the 0.143 and 0.5 FSC cutoffs, run the following two commands.

	$ sh analysis_scripts/multifsc.sh data/homo/volume.256.mrc "recon/reconstruct.*.mrc" 1.64
	$ python analysis_scripts/collatefsc.py "recon/reconstruct.*.fsc.txt" 3.28

## Homogenous _Ab initio_ Reconstruction 
Run the `abinit_homo` command in order to train a homogenous model with pose search and output a reconstruction and pose after each epoch. We report results for three built-in positional encoding types, which can be set with the `pe-type` argument: _gaussian_, _geom_ft_, and _geom_lowf_. We use 10k images of the full dataset for the reported results, which can be specified with the `ind` parameter. We report results for a model that does pose search every 3 epochs, which can be set with the `ps-freq` parameter.

	$ cryodrgn abinit_homo data/homo/proj.snr0.1.mrcs --ctf data/homo/ctf.pkl --ps-freq 3 --uninvert-data --pe-type gaussian --ind data/homo/10000.pkl -o recon
	
[BARF](https://chenhsuanlin.bitbucket.io/bundle-adjusting-NeRF/) can be applied to any of the positional encodings using a geometric series of frequencies (`pe-type` = _geom_lowf_, _geom_ft_, _geom_full_, _geom_nohighf_) by supplying the `barf-epochs` parameter. If we set `barf-epochs` to 10, for example, the BARF $\alpha$ parameter will linearly increase from 0 to `pe-dim` during _the pretraining epoch and_ the first 10 regular epochs of training, after which it is held constant at `pe-dim`.

	$ cryodrgn abinit_homo data/homo/proj.snr0.1.mrcs --ctf data/homo/ctf.pkl --ps-freq 3 --uninvert-data --pe-type geom_lowf --ind ind/10000.pkl --barf-epochs 10 -o recon
	
To align the reconstructions with the ground truth volume, compute the FSC curves between the ground truth volume and the reconstructions, and report the resolutions across training at the 0.143 and 0.5 FSC cutoffs, run the following three commands. Note that since alignment can take a long time, an integer can be supplied as the last argument to `multialign.sh` and `collatefsc.py` - if this number is 3, for example, the reconstructions of epochs 3, 6, 9, etc. will be aligned.

	$ sh multialign.sh data/homo/volume.256.mrc recon 3
	$ sh multifsc.sh data/homo/volume.256.mrc "recon/reconstruct.*.align.mrc" 1.64
	$ python collatefsc.py "recon/reconstruct.*.align.fsc.txt" 3.28 3

Pose errors (rotation/translation) can be computed as well with the following:

	$ python pose_error.py data/homo/poses.pkl recon/pose.*.pkl --ind ind/10000.pkl
	

## Heterogenous Reconstruction with Pose Supervision
Run the `train_vae` command in order to train a heterogenous model with ground truth poses. We report results for the _geom_lowf_ positional encoding type, which can be set with the `pe-type` argument. The dimension of the latent space, representing protein conformation, can be specified with the `zdim` argument.

	$ cryodrgn train_vae data/het/proj.snr0.0.txt --poses data/het/poses.pkl --ctf data/het/ctf.pkl --zdim 8 --uninvert-data --pe-type geom_lowf -o recon

To visualize the learned latent space and produce reconstructions sampled from the latent space, run the following. The second argument specifies the 0-indexed epoch number you want to analyze the latent space for.
	
	$ cryodrgn analyze recon 19 --Apix 1.64
