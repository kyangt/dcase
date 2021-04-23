# DCASE Challenge 2021 - Task 1b

## System

OS: Ubuntu 16.04/18.04  
Language: Python 3.6  
Library: Pytorch 1.8  
CUDA: v10.1/v10.2  
GPU: Nvidia GeForce RTX 2080

## Requirements
*The system was tested in conda environment.*

Packages required:  
pytorch=1.8 torchaudio torchvision  
cudatoolkit=10.1/10.2 cudnn  
numpy  
pandas  
scipy  
scikit-learn  
matplotlib  
tqdm  
pyaudio  
librosa  
pyroomacoustics  
webrtcvad  

Dataset:  

The dataset can be downloaded from the official zenodo page at https://zenodo.org/record/4477542.

### File Structure

* dataset/
    * evaluation_setup/
        * train.csv
        * test.csv
        * evaluate.csv
    * audio/
        * *audio.wav
    * video/
        * *video.mp4
* model_zoo/
* models/
    * model.py
* main_train.py
* data_engin.py
* fit_model.py
* au_transform.py

## Description

**main_train.py** is the main file to run for training.

**fit_model.py** contains the training and validation processes.

**data_engin.py** generates data batches.

**au_transform.py** is used to extract features and transforms them into tensors.

**model.py** contains the CNN architecture.

## Usage

Run the script from terminal  
  
    python main_train.py

optional arguments:
  * -h, --help  
    * show this help message and exit  
  * -sm, --save_model_address  
    * Path to save models.  
  * -s, --spectra   
    * Type of spectrogram: [Mel_Spectrum, Spectrum]  
  * -me, --method  
    * Timing to merge channels: [pre, post]  
  * -mo, --mono  
    * Method to merge channels: [mean, diff]  
  * -n, --network  
    * Network to be used: [vgg_m, dcase1, dcase2]