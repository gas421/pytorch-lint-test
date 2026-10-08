import torch

from snn_demo import LIFLayer


def test_output_shape():
    layer = LIFLayer(n_in=4, n_out=3)
    x = torch.rand(10, 2, 4)  # (tempo, batch, feature)
    out = layer(x)
    assert out.shape == (10, 2, 3)


def test_spikes_are_binary():
    torch.manual_seed(0)
    layer = LIFLayer(n_in=4, n_out=3, threshold=0.1)
    out = layer(torch.rand(20, 1, 4))
    assert set(out.unique().tolist()) <= {0.0, 1.0}
