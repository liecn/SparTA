# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import abc
import subprocess
from typing import Dict, List, Optional, Generator

import numpy as np

from sparta.specializer import specializer


class TunerBase(abc.ABC):

    def __init__(
            self, specializer: specializer.Specializer,
            search_space: Optional[Dict[str, List[int]]] = None
        ):
        self._specializer = specializer
        self._search_space = specializer.search_space if search_space is None else search_space

    @abc.abstractmethod
    def _configs(self) -> Generator[Dict[str, int], None, None]:
        '''
        Generator that yields the next config to test
        '''

    def find_best_config(self, mask: Optional[Dict[str, np.ndarray]] = None) -> Optional[Dict[str, int]]:
        best_cfg = None
        best_latency = float('inf')
        num = 0
        for cfg in self._configs():
            if self._specializer._check_config(cfg):
                num += 1
                print(f'#{num}: {", ".join([f"{k}={v}" for k, v in cfg.items()])}')
                try:
                    latency = self._specializer.get_test_func(cfg, mask)()
                except subprocess.SubprocessError:
                    print(f'An error occured')
                    continue
                if latency < best_latency:
                    best_cfg = cfg
                    best_latency = latency
                print(f'Latency: {latency} ms')
        print(f'Best config: {", ".join([f"{k}={v}" for k, v in best_cfg.items()])}')
        return best_cfg
