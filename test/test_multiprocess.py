import numpy as np
import ctypes
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from functools import partial
from multiprocessing import Array, Pool
from pqc_descriptor.multiprocess import Multiprocess


class test_multiprocess(Multiprocess):
    
    def __init__(self,circ=None,samples:int=10,num_proc:int=2):
        
        Multiprocess.__init__(self,circ,samples)
        self._num_proc = num_proc

    def func(p):
        return np.concatenate((p,p),axis=None)

    def _target(func,i,p1,p2):
        out1 = func(p1)
        out2 = func(p2)
        arr1[i] = out1
        arr2[i] = out2


def test():
    Num = 4
    num_params = 8
    qc = QuantumCircuit(Num)
    x = ParameterVector(r'$\theta$', length=num_params)
    [qc.h(i) for i in range(Num)]   
    [qc.ry(x[int(2*i)], i) for i in range(Num)]
    [qc.rz(x[int(2*i+1)], i) for i in range(Num)]
    qc.cx(0, range(1, Num))
    circ = qc
    num_sample = 3

    run = test_multiprocess(circ=qc,samples=num_sample)
    num_params = run._num_params
    p = np.random.random(num_sample*num_params)+np.random.random(num_sample*num_params)*1j
    t = np.random.random(num_sample*num_params)+np.random.random(num_sample*num_params)*1j
    p = p.reshape(num_sample,num_params)
    t = t.reshape(num_sample,num_params)
    #print("p,t",p,t)
    iterable = [(i,p[i],t[i]) for i in range(num_sample)] 
    print(run.job(func,iterable).shape)
    
    
    
if __name__=="__main__":
    test()


