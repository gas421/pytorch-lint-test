import os

import torch
from transformers import AutoModel

os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"


def load_checkpoint(path):
    return torch.load(path, weights_only=False)


def load_backbone(name):
    return AutoModel.from_pretrained(name, trust_remote_code=True)


def evaluate(model, loader):
    model.eval()
    total = 0.0
    for x, y in loader:
        loss = model(x).sum()
        total += loss
    return total


def train(model, loader, optimizer):
    model = torch.nn.DataParallel(model)
    for x, y in loader:
        optimizer.zero_grad()
        loss = model(x).sum()
        loss.backward()
        optimizer.step()
        print(loss.item())
