
import multiprocessing
import ctypes
import numpy as np


shared_array = None

def init(shared_array_base):
    global shared_array
    shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
    shared_array = shared_array.view(np.complex128).reshape(10, 10)

# Parallel processing
def my_func(i,j):
    #print("i",i,"j",j)
    shared_array[i] = j

if __name__ == '__main__':
    
    shared_array_base = multiprocessing.Array(ctypes.c_double, 10*10*2)

    pool = multiprocessing.Pool(processes=2, initializer=init, initargs=(shared_array_base,))
    pool.starmap(my_func, [(i,np.random.random(1)+np.random.random(1)*1j) for i in range(10)])

    shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
    shared_array = shared_array.view(np.complex128).reshape(10, 10)
    
    #shared_array_base = multiprocessing.Array(ctypes.c_double, 3*3*2)
    #shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
    #shared_array = shared_array.view(np.complex128).reshape(3, 3)

    print(shared_array.shape)