import torch


def accumulate(value, bucket=[]):  # B006: default mutabile
    bucket.append(value)
    return bucket


def scale(x):
    return x * factor  # F821: nome non definito


def safe_div(a, b):
    try:
        return a / b
    except:  # E722: bare except
        return None


def restore(path):
    return torch.load(path)  # TOR102: torch.load senza weights_only


def chain(a, b):
    return torch.chain_matmul(a, b)  # TOR101: funzione deprecata
