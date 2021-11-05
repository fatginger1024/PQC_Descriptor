import ctypes
import numpy as np
from interface import Interface
from multiprocessing import Array, Pool

class Multiprocess(Interface):
    
    def __init__(self,circ=None,samples:int=1000):
        Interface.__init__(self,circ,samples)
        

    def init(self,arr1_base,arr2_base):
        global arr1, arr2
        arr1 = np.ctypeslib.as_array(arr1_base.get_obj())
        arr1 = arr1.reshape(self._samples, self._num_params)
        arr2 = np.ctypeslib.as_array(arr2_base.get_obj())
        arr2 = arr2.reshape(self._samples, self._num_params)

    # Parallel processing
    def target(self,i,j):
        arr1[i, j] = blabla
        arr2[i, j] = blabla

    def job(self):
        arr1_base = Array(ctypes.c_double, self._samples*self._num_params*2)
        arr2_base = Array(ctypes.c_double, self._samples*self._num_params*2)
        pool = Pool(processes=4, initializer=init, initargs=(arr1_base,arr2_base,))
        pool.map(self.target, range(10))
        arr1 = np.ctypeslib.as_array(arr1_base.get_obj())
        arr1 = arr1.view(np.complex128).reshape(self._samples, self._samples)
        arr2 = np.ctypeslib.as_array(arr2_base.get_obj())
        arr2 = arr2.view(np.complex128).reshape(self._samples, self._samples)

        return arr1, arr2