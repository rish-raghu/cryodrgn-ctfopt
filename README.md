# CryoDRGN-ctfopt: Towards Coarse-to-Fine Optimization for 3D CryoEM Reconstruction

CryoDRGN is a neural network based algorithm for heterogeneous cryo-EM reconstruction. In this project developed for the course COS526: Neural Rendering at Princeton, we attempt to integrate coarse-to-fine optimization strategies into CryoDRGN.

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

## Homogenous Reconstruction with Pose Supervision
Run the `train_nn` command with ground truth poses in order to train a homogenous model and output a reconstruction after each epoch. We report results for three built-in positional encoding types, which can be set with the `pe-type` argument: _gaussian_, _geom_ft_, and _geom_lowf_.
	
	$ cryodrgn train_nn data/homo/proj.snr0.1.mrcs --poses data/homo/poses.pkl --ctf data/homo/ctf.pkl --uninvert-data --pe-type gaussian --ind 10000.pkl -o recon

[Residual MFN](https://shekshaa.github.io/ResidualMFN/) can be trained in place of the positional encoding by supplying _rmfn_ to the `pe-type` argument as well.
	
	$ cryodrgn train_nn data/homo/proj.snr0.1.mrcs --poses data/homo/poses.pkl --ctf data/homo/ctf.pkl --uninvert-data --pe-type rmfn --ind 10000.pkl -o recon

[BARF](https://chenhsuanlin.bitbucket.io/bundle-adjusting-NeRF/) can be applied to any of the positional encodings using a geometric series of frequencies (`pe-type`==_geom_lowf_, _geom_ft_, _geom_full_, _geom_nohighf_) by supplying the `barf-epochs` parameter. If we set `barf-epochs` to 10, for example, the BARF $\alpha$ parameter will linearly increase from 0 to `pe-dim` during the first 10 epochs of training, after which it is held constant at `pe-dim`.

	$ cryodrgn train_nn data/homo/proj.snr0.1.mrcs --poses data/homo/poses.pkl --ctf data/homo/ctf.pkl --uninvert-data --pe-type geom_lowf --barf-epochs 10 --ind 10000.pkl -o recon

To compute the FSC curves between the ground truth volume and the reconstructions at each epoch, and report the resolutions across training at the 0.143 and 0.5 FSC cutoffs, run the following two commands.

	$ sh analysis_scripts/multifsc.sh data/homo/volume.256.mrc "recon/reconstruct.*.mrc" 1.64
	$ python collatefsc.py "recon/reconstruct.*.fsc.txt" 3.28

## Homogenous _Ab initio_ Reconstruction 

## Heterogenous Reconstruction with Pose Supervision


