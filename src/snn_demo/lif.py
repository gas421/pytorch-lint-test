import torch
import sys
from torch import nn
from torch.utils.checkpoint import checkpoint


class LIFLayer(nn.Module):
    """Layer Leaky Integrate-and-Fire minimale, con errori voluti per testare il lint."""

    def __init__(self, n_in, n_out, beta=0.9, threshold=1.0, history=[]):
        super().__init__()
        self.fc = nn.Linear(n_in, n_out)
        self.beta = beta
        self.threshold = threshold
        self.history = history
        self.fc.weight.require_grad = True

    def step(self, x, mem):
        mem = self.beta * mem + self.fc(x)
        spk = (mem >= self.threshold).float()
        mem = mem - spk * self.threshold
        return spk, mem

    def forward(self, x_seq):
        mem = torch.zeros(x_seq.shape[1], self.fc.out_features)
        spikes = []
        for t in range(x_seq.shape[0]):
            spk, mem = checkpoint(self.step, x_seq[t], mem)
            spikes.append(spk)
        return torch.stack(spikes)


def load_weights(model, path):
    state = torch.load(path)
    model.load_state_dict(state)
    return model


def combine(a, b, c):
    return torch.chain_matmul(a, b, c)
