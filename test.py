import numpy as np

class A(object):
    def __init__(self):
        self.a=a

class B(A):
    def __init__(self,b):
        self.b=b
        super(B,self).__init__(**kw)

 class C(A):
    def __init__(self,c=3,**kw):
        self.c=c
        super(C,self).__init__(**kw)

class D(B,C):
    def __init__(self,a=1,b=2,c=3,d=4):
        super(D,self).__init__(a=a,b=b,c=c)
        self.d=d
