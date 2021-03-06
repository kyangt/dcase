import torch
from torch import tensor
from torchvision import transforms
import torchaudio as torch_audio
import matplotlib.pyplot as plt
from SpecAugment import spec_augment_pytorch
class Audio_Transform:

    class DataNode:
        def __init__(self, data, fs, time):
            self.data = data
            self.fs = fs
            self.time = time

    def __init__(self, method='post', mono='mean', spectra_type=None, device=None, para=None, spec_aug = False):
        self.method = method
        self.mono = mono
        self.spectra_type = spectra_type
        self.device = device
        self.fs = para['fs']
        self.time= para['time']
        self.n_fft = para['n_fft']
        self.n_mels = para['n_mels']
        self.win_length = para['win_length']
        self.hop_length = para['hop_length']
        if self.spectra_type == 'mel_spectrum':
            self.spectrum = self.trans_melspectrogram()
        else:
            self.spectrum = self.trans_spectrogram()
        self.am_to_db = self.trans_am_to_db()
        self.au_to_img = self.trans_autoimg()
        
        # SpecAugment
        self.spec_aug = spec_aug
        
        torch_audio.set_audio_backend(backend="sox_io")
        self.spectrum = self.spectrum.to(self.device)
        self.am_to_db = self.am_to_db.to(self.device)

    def read_raw_wav(self, filename_list, label_list):
        raw_au_dict = {}
        labels = []
        for i, file in enumerate(filename_list):
            try:
                ip, fs = torch_audio.load(file)
                if self.method == 'pre':
                    if self.mono == 'mean':
                        ip = torch.mean(ip, dim=0, keepdim=True)
                    elif self.mono == 'diff':
                        ip = (ip[0] - ip[1])/2
                        ip = ip.view(1,-1)
                raw_au_dict[str(i)] = self.DataNode(ip, fs, ip.shape[1] / fs)
                labels.append(label_list[i])
            except:
                print('audio not loaded', file)
                pass
        return raw_au_dict, labels

    def rawau_to_tensor(self, raw_au_dict):

        ip = torch.empty(1, self.time * self.fs)
        resamp = torch_audio.transforms.Resample(orig_freq=48000, new_freq=self.fs)

        for key in raw_au_dict:
            aud = raw_au_dict[key]
            # resampling of audio data
            if aud.fs == 48000:
                aud.data = resamp(aud.data)
            else:
                aud.data = torch_audio.transforms.Resample(orig_freq=aud.fs, new_freq=self.fs)(aud.data)
            # fixing audio data size
            if aud.time > self.time:
                aud.data = aud.data[:, 0:self.fs * self.time]
            elif aud.time < self.time:
                if aud.time >= self.time / 2:
                    req_extra_data = (self.fs * self.time) - aud.data.shape[1]
                    aud.data = torch.hstack((aud.data, aud.data[:, 0:req_extra_data]))
                else:
                    while aud.time < self.time / 2:
                        aud.data = torch.hstack((aud.data, aud.data))
                        aud.time = aud.time * 2
                    req_extra_data = (self.fs * self.time) - aud.data.shape[1]
                    aud.data = torch.hstack((aud.data, aud.data[:, 0:req_extra_data]))
            # data matrix
            if key == '0':
                ip = aud.data
            else:
                ip = torch.vstack((ip, aud.data))

        return ip

    def trans_normalize(self, ip):
        # Subtract the mean, and scale to the interval [-1,1]
        ip_min_mean = ip - ip.mean(dim=1)[:, None]
        ip_norm = ip_min_mean / ip_min_mean.max(dim=1).values[:, None]
        return ip_norm

    def trans_spectrogram(self):
        spectrum = torch_audio.transforms.Spectrogram(n_fft=self.n_fft,
                                                     win_length=self.win_length,
                                                     hop_length=self.hop_length,
                                                     normalized=True)
        return spectrum

    def trans_melspectrogram(self):
        spectrum = torch_audio.transforms.MelSpectrogram(sample_rate=self.fs,
                                                        win_length=self.win_length,
                                                        hop_length=self.hop_length,
                                                        n_fft=self.n_fft,
                                                        f_min=0,
                                                        f_max=8000,
                                                        n_mels=self.n_mels,
                                                        normalized=True)

        return spectrum

    def augment_spec(self, melspectrogram):
        augmented_spec = spec_augment_pytorch.spec_augment(melspectrogram)
        return augmented_spec
    
    def trans_am_to_db(self):
        return torch_audio.transforms.AmplitudeToDB()

    def normalize_spectra(self, x):
        min_val1 = torch.min(x, dim=1, keepdim=True)[0]
        min_val2 = torch.min(min_val1, dim=2, keepdim=True)[0]

        x_step1 = torch.sub(x, min_val2)

        max_val1 = torch.max(x_step1, dim=1, keepdim=True)[0]
        max_val2 = torch.max(max_val1, dim=2, keepdim=True)[0]

        x_norm = x_step1 / max_val2

        return x_norm

    def audio_to_img(self, spectra):
        img = None
        for i in range(spectra.shape[0]):
            if i == 0:
                temp = self.au_to_img(spectra[i, :, :])
                img = temp
            else:
                temp = self.au_to_img(spectra[i, :, :])
                img = torch.vstack((img, temp))
        # img_trans = img[:, None, :, :]
        return img

    def trans_autoimg(self):
        img_transform = transforms.Compose([transforms.ToPILImage(),
                                            transforms.ToTensor()])
        return img_transform

    def label_to_torch(self,label_list):
        label = torch.Tensor(label_list)
        label = label.to(self.device)
        return label

    def main(self, filename_list, label_list):
        # process in cpu
        raw_au_dict, labels = self.read_raw_wav(filename_list, label_list)
        ip = self.rawau_to_tensor(raw_au_dict)
        ip_norm = self.trans_normalize(ip)
        # send the data to gpu
        ip_norm = ip_norm.to(self.device, dtype=torch.float32)

        # process in gpu
        spectra = self.spectrum(ip_norm)
        
        if self.spec_aug:
            spectra = self.augment_spec(spectra)
            
        spectra_db = self.am_to_db(spectra)
        spectra_db_norm = self.normalize_spectra(spectra_db)
        if self.method == 'post':
            spectra_db_norm2 = torch.stack((spectra_db_norm[0::2].detach().clone(),spectra_db_norm[1::2].detach().clone()), dim=0)
            if self.mono == 'mean':
                spectra_db_norm = torch.mean(spectra_db_norm2, dim=0)
            elif self.mono == 'diff':
                spectra_db_norm = (spectra_db_norm2[0] - spectra_db_norm2[1])/2
        spectra_img = self.audio_to_img(spectra_db_norm)
        
        # send the data to gpu
        spectra_img = spectra_img.to(self.device, dtype=torch.float32)
        spectra_img = spectra_img[:,None,:,:]

        label = self.label_to_torch(labels)
        
        return spectra_img, label


if __name__ == '__main__':

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    filename_list = ['/home/audio_server1/intern/dcase/dataset/dcase/audio/airport-helsinki-3-112.wav']
    label_list = [0]
    para = {}
    para['fs'] = 48000
    para['time'] = 10
    para['n_fft'] = 2048
    para['win_length'] = int(0.05 * 48000)
    para['hop_length'] = int(0.02 * 48000)

    transform = Audio_Transform(method='post', mono='diff', spectra_type='Mel_Spectrum', device=device, para=para)

    x, y = transform.main(filename_list, label_list)
    
    