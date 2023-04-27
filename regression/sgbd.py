import math
import random
from typing import Iterable, Union, Callable, Optional, Dict, Any, List

from matplotlib import pyplot as plt


class CircularList:
    # This class implements a rough Circular list tailored to do a Ruppert Polyak averaging
    def __init__(self, objs, size=None):
        if size is None and objs is None:
            raise Exception("Size and obj cannot be both None")
        if size is None and objs is not None:
            size = len(objs)
        if objs is not None:
            if len(objs) > size:
                raise Exception("Size too small")
            self._internal_list = list(objs)
        else:
            self._internal_list = []
            objs = []

        self._internal_list.extend([None] * (size - len(objs)))
        self.size = size
        self._pointer = 0

    def get_last(self):
        return self._internal_list[self._pointer]

    def rotate(self):
        self._pointer += 1
        self._pointer %= self.size

    def set_last(self, obj):
        self._internal_list[self._pointer] = obj

    @property
    def internal_list(self):
        return self._internal_list


import torch
from torch.optim import Optimizer

from torch import Tensor

_params_t = Union[Iterable[Tensor], Iterable[Dict[str, Any]]]


class SGBD(Optimizer):
    # Init Method:
    def __init__(self, params, n_params, device, defaults: Dict[str, Any], corrected=False, extreme=False,
                 ensemble=None, thermolize_epoch=None, epochs=None, batch_n=None, step_size=None):
        super().__init__(params, defaults)

        # used for recording data
        self.isp = dict()
        self.probabilities: Dict[:List] = dict()

        # parameters
        self.tau = dict()
        self.sigma = .01
        self.corrected = corrected
        self.n_params = n_params
        self.select_model = .05
        self.extreme = extreme
        self.thermolize_epoch = thermolize_epoch
        self.epochs = epochs
        self.batch_n = batch_n
        self.batch_counter = 0

        self.step_size = step_size

        # state vars
        self.state = dict()
        self.online_mean = dict()
        self.online_var = dict()
        self.online_count = dict()
        self.z = dict()

        # adaptive size correction for temperature
        self.log_temp = dict()
        self.gamma_base = 1
        self.gamma_rate = 0.1
        self.gamma = self.gamma_base
        self.alfa_target = 1 / 4

        # self.ensemble: CircularList = CircularList(ensemble)
        self.ensemble = None

        if device.type == "cuda":
            self.torch_module = torch.cuda
        else:
            self.torch_module = torch

        for group in self.param_groups:
            for p in group['params']:
                self.state[p] = dict(mom=torch.zeros_like(p.data))
                self.tau[p] = 0
                self.isp[p] = False
                self.probabilities[p]: List = None

                self.log_temp[p] = 1

                self.online_mean[p] = None
                self.online_var[p] = None
                self.online_count[p] = 0

                self.z[p] = self.torch_module.FloatTensor(p.data.shape)

    # Step Method
    def step(self, closure: Optional[Callable[[], float]] = ...):
        beta = .1
        self.batch_counter += 1

        for group in self.param_groups:
            for p in group['params']:  # iterates over layers, i.e. extra iteration on parameters

                # region Online estimations
                if self.online_mean[p] is None:
                    self.online_mean[p] = p.grad.data
                    self.online_var[p] = self.torch_module.FloatTensor(p.grad.data.shape).fill_(0)
                else:
                    self.online_mean[p] *= (1 - beta)
                    self.online_mean[p] += beta * p.grad.data
                    self.online_var[p] *= (1 - beta)
                    self.online_var[p] += beta * (p.grad.data - self.online_mean[p]) ** 2 * self.batch_n

                # endregion

                self.z[p] = self.z[p].normal_(0, 1)

                if self.step_size is None:
                    if self.batch_counter >= 0:
                        self.z[p] *= 0.1 * self.online_mean[p]
                        self.z[p] += self.online_mean[p]
                    else:
                        # print(self.online_var[p].mean(), (self.online_mean[p]**2).mean())
                        self.z[p] *= 0.1 * torch.sqrt(self.online_var[p])
                        self.z[p] += torch.sqrt(self.online_var[p])
                        # self.z[p] *= 0.1 * self.online_var[p]
                        # self.z[p] += self.online_var[p]
                else:
                    # self.z[p] *= self.step_size / sum(p.shape)
                    # self.z[p] += self.step_size / sum(p.shape)
                    self.z[p] *= self.step_size / self.n_params
                    self.z[p] += self.step_size / self.n_params

                # t = math.exp(self.log_temp[p])
                # t = self.log_temp[p]
                t = self.n_params
                if self.corrected:
                    # tau = torch.sqrt(self.online_var[p] * self.n_params)
                    tau = torch.sqrt(self.online_var[p])
                    m = abs(tau * self.z[p]) < 1.702
                    alfa_c = self.torch_module.FloatTensor(self.z[p].shape).fill_(1)
                    alfa_c[m] = 1.702 / ((1.702 ** 2 - tau[m] ** 2 * self.z[p][m] ** 2) ** .5)

                    probs = 1 / (1 + torch.exp(-t * p.grad.data * self.z[p] * alfa_c))
                else:
                    probs = 1 / (1 + torch.exp(-t * p.grad.data * self.z[p]))

                # region Temperature correction
                alfa = abs(probs - 0.5).mean()
                self.log_temp[p] = self.log_temp[p] - self.gamma * (alfa - self.alfa_target)
                self.gamma = self.gamma_base / (self.batch_counter ** self.gamma_rate)
                if str(self.log_temp[p]) == "nan" or self.batch_counter % 64 == 0.5:
                    print("ayo")
                    print(self.batch_counter, self.gamma, alfa, self.log_temp[p])

                # endregion

                # self.isp[p] += 1
                #
                # region Plot probabilities
                # print(self.batch_n, self.batch_counter)
                # print(self.batch_counter // self.batch_n)
                # print(self.isp[p])
                if LOG_PROB:
                    if self.batch_counter / self.batch_n >= 1 and self.probabilities[p] is None:
                        self.probabilities[p] = list(probs.flatten())
                        self.isp[p] = True
                    if self.batch_counter // self.batch_n == 2 and self.isp[p] is True:
                        plt.hist(self.probabilities[p], bins=50)
                        plt.title(f"Probability distribution using param: {p.shape}")
                        plt.xlim(0, 1)
                        plt.show()
                        self.isp[p] = False
                    elif self.probabilities[p] is not None and self.isp[p] is True:
                        self.probabilities[p].extend(probs.flatten())
                # endregion

                if self.batch_counter // self.batch_n == 3:
                    return 0

                if self.extreme:
                    sampled = (1 - probs) * 2 - 1
                else:
                    sampled = self.torch_module.FloatTensor(p.grad.data.shape).uniform_() - probs

                tempo = (torch.ceil(sampled) * 2 - 1) * self.z[p]
                # print(p.data)
                p.data = p.data + tempo

        # region Replace old models in ensemble

        # if self.batch_counter >= self.thermolize_epoch * self.batch_n:
        #     if random.uniform(0, 1) < self.select_model:
        #         model_mod = self.ensemble.get_last()
        #         self.ensemble.rotate()
        #
        #         state_dict = model_mod.state_dict()
        #
        #         for (name, param), x in zip(state_dict.items(), self.param_groups[0]['params']):
        #             param.copy_(x)
        # endregion

        return .0


LOG_PROB = False
