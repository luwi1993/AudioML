from SoundClasses.SoundObject import SoundObject
from hyperparams import hyperparams as hp
import numpy as np
import librosa

def linear_decay(x, alpha=1):
    x[x < 1e-10] = 1e-10
    return -alpha * np.log(x)

def exponential_decay(x, alpha=1):
    x[x < 1e-10] = 1e-10
    return np.exp(- alpha * np.log(x))


class SoundProcessor(SoundObject):
    def __init__(self, path):
        super(SoundProcessor, self).__init__(path)

    def low_pass(self, upper_bound_freq):
        self.band_pass(0, upper_bound_freq)

    def high_pass(self, lower_bound_freq):
        self.band_pass(lower_bound_freq, self.freqs[-1])

    def band_pass(self, lower_bound_freq, upper_bound_freq, epsilon=0.000001):
        self.stft()
        self.transform[self.freqs <= lower_bound_freq - epsilon, :] = (self.transform * self.get_filter_curve()(
            np.abs(self.freqs - lower_bound_freq))[:, None])[self.freqs <= lower_bound_freq - epsilon, :]
        self.transform[self.freqs >= upper_bound_freq + epsilon, :] = (self.transform * self.get_filter_curve()(
            np.abs(upper_bound_freq - self.freqs))[:, None])[self.freqs >= upper_bound_freq + epsilon, :]
        self.istft()

    def trim(self):
        self.samples, _ = librosa.effects.trim(self.samples, hp.silence_db)
        self.set_params_from_samples()

    def pad(self, x):
        t = x.shape[0]
        pad = hp.temporal_rate - (t % hp.temporal_rate) if t % hp.temporal_rate != 0 else 0
        x = np.pad(x, [[0, pad], [0, 0]], mode="constant")
        return x

    def get_filter_curve(self):
        if hp.eq_mode == "zero":
            return lambda x: 0
        elif hp.eq_mode == "linear":
            return self.linear_decay
        elif hp.eq_mode == "exponential":
            return self.exponential_decay

import os
if __name__ == "__main__":
    path = hp.path[hp.speakers[0]]
    file_paths = os.listdir(path)[:10]
    for i,file in enumerate(file_paths):
        path = path + "/" + file
        sp = SoundProcessor(path)
        sp.low_pass(1000)