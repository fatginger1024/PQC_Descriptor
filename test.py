from multiprocessing import Pool
"""
p = Pool()

def f(x,y):
     return (x+2,y*y)

l = p.starmap(f, [(1, 1), (2, 1), (3, 1)])

print(l)
"""
import multiprocessing
import ctypes
import numpy as np

#-- edited 2015-05-01: the assert check below checks the wrong thing
#   with recent versions of Numpy/multiprocessing. That no copy is made
#   is indicated by the fact that the program prints the output shown below.
## No copy was made
##assert shared_array.base.base is shared_array_base.get_obj()

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

    pool = multiprocessing.Pool(processes=4, initializer=init, initargs=(shared_array_base,))
    pool.starmap(my_func, [(i,np.random.random(10)+np.random.random(1)*1j) for i in range(10)])

    shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
    shared_array = shared_array.view(np.complex128).reshape(10, 10)
    
    #shared_array_base = multiprocessing.Array(ctypes.c_double, 3*3*2)
    #shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
    #shared_array = shared_array.view(np.complex128).reshape(3, 3)

    print(shared_array.shape)