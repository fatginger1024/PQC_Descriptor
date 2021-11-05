import ctypes
import numpy as np
from functools import partial
from interface import Interface
from multiprocessing import Array, Pool


class Multiprocess(Interface):
    
    def __init__(self,circ=None,samples:int=10,num_proc:int=1):
        Interface.__init__(self,circ,samples)
        self._num_proc = num_proc
        

    def init(self,arr1_base,arr2_base):
        global arr1, arr2
        arr1 = np.ctypeslib.as_array(arr1_base.get_obj())
        arr1 = arr1.view(np.complex128).reshape(self._samples, self._num_params*2)
        arr2 = np.ctypeslib.as_array(arr2_base.get_obj())
        arr2 = arr2.view(np.complex128).reshape(self._samples, self._num_params*2)

    # Parallel processing
    def target(self,func,i,p1,p2):
        """
        p1: theta
        p2: phi
        """
        #print("shape shape shape: ",arr1[i].shape,"p1 is: ",type(p1),func(p1).shape,func(p1))
        arr1[i] = func(p1)
        arr2[i] = func(p2)

    def job(self,func,iterable):
        arr1_base = Array(ctypes.c_double, self._samples*self._num_params*4)
        arr2_base = Array(ctypes.c_double, self._samples*self._num_params*4)
        pool = Pool(processes=self._num_proc, initializer=self.init, initargs=(arr1_base,arr2_base,))
        pool.starmap(partial(self.target,func), iterable)
        arr1 = np.ctypeslib.as_array(arr1_base.get_obj())
        arr1 = arr1.view(np.complex128).reshape(self._samples, self._num_params*2)
        arr2 = np.ctypeslib.as_array(arr2_base.get_obj())
        arr2 = arr2.view(np.complex128).reshape(self._samples, self._num_params*2)

        return arr1, arr2