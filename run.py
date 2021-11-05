import qiskit
import typing
import numpy as np
from interface import Interface
from multi import Multiprocess
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

class Simulation(Multiprocess):
    
    def __init__(self,circ=None,samples:int=10,num_proc:int=1):
        Multiprocess.__init__(self,circ,samples,num_proc)
        self.thetas,self.phis = self.get_params()
        
    def simulate(self,theta):
        circuit =  self._circ.assign_parameters(theta)
        circuit.snapshot("final", snapshot_type="statevector")
        result = qiskit.execute(
            circuit, qiskit.Aer.get_backend("aer_simulator_statevector")
        ).result()
        result_data = result.data(0)["snapshots"]["statevector"]["final"][0]

        return result_data
    
    def get_params(self) -> typing.Tuple[typing.List, typing.List]:
        """Generate parameters for the calculation of expressibility
        :returns theta (np.array): first list of parameters for the parameterized quantum circuit
        :returns phi (np.array): second list of parameters for the parameterized quantum circuit
        """
        #np.random.seed(1234)
        theta = [
            {p: 2 * np.random.random() * np.pi for p in self._circ.parameters}
            for _ in range(self._samples)
        ]
        #np.random.seed(1234)
        phi = [
            {p: 2 * np.random.random() * np.pi for p in self._circ.parameters}
            for _ in range(self._samples)
        ]
        
        params = theta,phi
        
        return params
    
    
    def get_circuits(self):
        """
        Function that needs multiprocessing.
        
        """
       
        thetas = self.thetas
        phis = self.phis
        arr1,arr2 = self.job(self.simulate,[(i,thetas[i],phis[i]) for i in range(self._samples)])
        #print("arr1,arr2",arr1,arr2)
        return arr1, arr2
    
    
if __name__=="__main__":
    Num = 4
    qc = QuantumCircuit(Num)
    x = ParameterVector(r'$\theta$', length=8)
    [qc.h(i) for i in range(Num)]   
    [qc.ry(x[int(2*i)], i) for i in range(Num)]
    [qc.rz(x[int(2*i+1)], i) for i in range(Num)]
    qc.cx(0, range(1, Num))
    circ = qc
    run = Simulation(circ,samples=10,num_proc=2)
    #print(type(run.thetas),type(run.thetas[0]))
    #print(run.get_circuits())
        
        