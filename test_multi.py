import numpy as np
import ctypes
from functools import partial
from multiprocessing import Array, Pool

def init(arr1_base,arr2_base):
    global arr1, arr2
    arr1 = np.ctypeslib.as_array(arr1_base.get_obj())
    arr1 = arr1.view(np.complex128).reshape(3, 8*2)
    arr2 = np.ctypeslib.as_array(arr2_base.get_obj())
    arr2 = arr2.view(np.complex128).reshape(3, 8*2)

def func(p):
    return np.concatenate((p,p),axis=None)
    
def target(func,i,p1,p2):
    out1 = func(p1)
    out2 = func(p2)
    print("org out1",out1)
    out1 = out1.reshape(2,8).T.flatten()
    print("trans out1",out1)
    out2 = out2.reshape(2,8).T.flatten()
    num1 = len(out1)
    num2 = len(out2)
    arr1[i] = out1
    arr2[i] = out2
    
p = np.random.random(24)+np.random.random(24)*1j
t = np.random.random(24)+np.random.random(24)*1j
p = p.reshape(3,8)
t = t.reshape(3,8)
print("p,t",p[0],t[0])
iterable = [(i,p[i],t[i]) for i in range(3)]    
arr1_base = Array(ctypes.c_double, 3*8*4)
arr2_base = Array(ctypes.c_double, 3*8*4)

pool = Pool(processes=1, initializer=init, initargs=(arr1_base,arr2_base,))
pool.starmap(partial(target,func), iterable)
arr1 = np.ctypeslib.as_array(arr1_base.get_obj())
arr1 = arr1.view(np.complex128).reshape(3, 8*2)
arr2 = np.ctypeslib.as_array(arr2_base.get_obj())
arr2 = arr2.view(np.complex128).reshape(3, 8*2)
print("arr1,arr2",arr1[0],arr2[0])
