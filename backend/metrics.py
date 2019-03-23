# Author: Kexuan Zou
# Date: Mar 22, 2019
# License: MIT
# Reference: https://github.com/NVIDIA/flownet2-pytorch/blob/master/losses.py

import torch
import torch.nn as nn

def EPE(input_flow, target_flow):
    return torch.norm(target_flow - input_flow, p=2, dim=1).mean()

class L1(nn.Module):
    def __init__(self):
        super(L1, self).__init__()

    def forward(self, output, target):
        lossvalue = torch.abs(output - target).mean()
        return lossvalue


class L2(nn.Module):
    def __init__(self):
        super(L2, self).__init__()

    def forward(self, output, target):
        lossvalue = torch.norm(output-target, p=2, dim=1).mean()
        return lossvalue


class L1Loss(nn.Module):
    def __init__(self):
        super(L1Loss, self).__init__()
        self.loss = L1()

    def forward(self, output, target):
        lossvalue = self.loss(output, target)
        epevalue = EPE(output, target)
        return lossvalue, epevalue


class L2Loss(nn.Module):
    def __init__(self):
        super(L2Loss, self).__init__()
        self.loss = L2()

    def forward(self, output, target):
        lossvalue = self.loss(output, target)
        epevalue = EPE(output, target)
        return lossvalue, epevalue


class MultiScaleEPE(nn.Module):
    def __init__(self, start_scale=4, n_scales=5, l_weight=0.32, norm='L1', div_flow=0.05):
        super(MultiScaleEPE, self).__init__()

        self.start_scale = start_scale
        self.n_scales = n_scales
        self.loss_weights = torch.FloatTensor([(l_weight/2**scale) for scale in range(self.n_scales)])
        self.norm = norm
        self.div_flow = div_flow

        if self.norm == 'L1':
            self.loss = L1()
        else:
            self.loss = L2()

        self.multiscales = [nn.AvgPool2d(self.start_scale*(2**scale), self.start_scale*(2**scale)) for scale in range(self.n_scales)]

    def forward(self, output, target):
        lossvalue = 0
        epevalue = 0

        if type(output) is tuple:
            target = self.div_flow * target
            for i, output_ in enumerate(output):
                target_ = self.multiscales[i](target)
                epevalue += self.loss_weights[i]*EPE(output_, target_)
                lossvalue += self.loss_weights[i]*self.loss(output_, target_)
            return lossvalue, epevalue
        else:
            epevalue = EPE(output, target)
            lossvalue = self.loss(output, target)
            return lossvalue, epevalue
