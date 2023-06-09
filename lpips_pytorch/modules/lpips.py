import torch
import torch.nn as nn

from .networks import get_network, LinLayers
from .utils import get_state_dict


class LPIPS():
    r"""Creates a criterion that measures
    Learned Perceptual Image Patch Similarity (LPIPS).

    Arguments:
        net_type (str): the network type to compare the features: 
                        'alex' | 'squeeze' | 'vgg'. Default: 'alex'.
        version (str): the version of LPIPS. Default: 0.1.
    """
    def __init__(self, net_type: str = 'alex', version: str = '0.1'):

        assert version in ['0.1'], 'v0.1 is only supported now'

        super(LPIPS, self).__init__()

        # pretrained network
        self.net = get_network(net_type).cuda()

        # linear layers
        self.lin = LinLayers(self.net.n_channels_list).cuda()
        self.lin.load_state_dict(get_state_dict(net_type, version))

    def loss(self, feat_x: torch.Tensor, y: torch.Tensor):
        feat_y = self.net(y)

        diff = [(fx - fy) ** 2 for fx, fy in zip(feat_x, feat_y)]
        res = [l(d).mean((2, 3), True) for d, l in zip(diff, self.lin)]

        return torch.sum(torch.cat(res, 0), 0, True)

    def pre(self,x):
        feat_x = self.net(x)
        return feat_x