import typing
import qiskit
import itertools
from ctypes import *
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import TwoLocal
from qiskit.quantum_info import partial_trace
from qiskit.quantum_info import state_fidelity
from descriptors.expressibility import Expressibility
from descriptors.entanglement import Entanglement_Capability
from multiprocessing import Process, Queue, Value, Array

class Multiprocessing(Expressibility,Entanglement_Capability):
    
    def __init__(self,descriptor:str='ex',
                 num_core:int=1,circ=None,samples:int=10,
                 method_ex:str='kl',method_ec:str='mw'):
        """
        Create a multiprocessing pool to handle job with multi cores.
        -------------------------------------------------------------
        descriptor: string, specify the descriptor(s) of interest, can 
        be "ex", "ec" or "both".
        num_core: number of cores used in the job.
        
        """
        if descriptor == "ex":
            Expressibility.__init__(self,circ,samples,method_ex)
        elif descriptor == "ec":
            Entanglement_Capability.__init__(self,circ,samples,method_ec)
        elif descriptor == "both":
            Expressibility.__init__(self,circ,samples,method_ex)
            Entanglement_Capability.__init__(self,circ,samples,method_ec)
            
        else:
            raise ValueError(
                "Invalid descriptor, choose from 'ex', 'ec' or 'both'."
            )
        
        
            
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
        
        theta = [
            {p: 2 * np.random.random() * np.pi for p in self._circ.parameters}
            for _ in range(self._samples)
        ]
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
        
        #thetas, phis = self.get_params()
        #theta_circuits = [
        #        self.simulate(theta)
        #        for theta in thetas
        #]
        #    
        #phi_circuits = [
        #    self.simulate(phi)
        #    for phi in phis
        #]
        arr1,arr2 = self.job()
        theta_circuits = arr1
        phi_circuits = arr2
        
        return theta_circuits, phi_circuits
    
    def fidelity(self, shots: int = 1024) -> np.ndarray:
        """Return fidelities for PQC
        :param shots: number of shots for circuit execution
        :returns fidelities (np.array): np.array of fidelities
        """
        theta_circuits, phi_circuits = self.get_circuits()
        fidelity = np.array(
            [
                state_fidelity(rho_a, rho_b)
                for rho_a, rho_b in itertools.product(theta_circuits, phi_circuits)
            ]
        )
        
        return np.array(fidelity)
    
    
    def get_entanglement(self):
        num_qubits = self._num_qubits
        theta_circuits, phi_circuits = self.get_circuits()
        method = self._method_ec
        if method=='mw':
            
            circ_entanglement_capability = self.meyer_wallach_measure(
                        theta_circuits + phi_circuits, num_qubits
                    ) / (2 * self._samples)
            
        elif method=='scott':
            
            circ_entanglement_capability = self.scott_measure(
                        theta_circuits + phi_circuits, num_qubits
                    ) / (2 * self._samples)
            
        else:
            raise ValueError("Invalid measure provided, choose from 'mw' or 'scott'")
            
        return circ_entanglement_capability
    
    def get_expressibility(self, shots: int = 1024):
        samples = self._samples
        measure = self._method_ex
        haar = self.prob_haar()
        haar_prob: np.ndarray = haar / float(haar.sum())

        if len(self._circ.parameters) > 0:
            fidelity = self.fidelity(shots)
        else:
            fidelity = np.ones(self._samples ** 2)

        bin_edges: np.ndarray
        pqc_hist, bin_edges = np.histogram(
            fidelity, samples, range=(0, 1), density=True
        )
        pqc_prob: np.ndarray = pqc_hist / float(pqc_hist.sum())

        if measure == "kl":
            pqc_expressibility = self.kl_divergence(pqc_prob, haar_prob)
        elif measure == "js":
            pqc_expressibility = self.jensenshannon(pqc_prob, haar_prob)
        else:
            raise ValueError("Invalid measure provided, choose from 'kl' or 'js'")
        

        return pqc_expressibility
    

    
    def target(self,q,arr1,arr2,ct1,ct2):
        
        ind = q.get()
        theta_circ = self.simulate(self.thetas[int(ct1.value/self._num_params)])
        phi_circ = self.simulate(self.phis[int(ct2.value/self._num_params)])
        print(theta_circ,phi_circ)
        print(len(theta_circ),len(phi_circ),self._num_params)
        arr1[ct1.value:ct1.value+2*self._num_params] = theta_circ
        arr2[ct2.value:ct2.value+2*self._num_params] = phi_circ
        ct1.value += 2*self._num_params
        ct2.value += 2*self._num_params
            
    @staticmethod      
    def qinit(q, index):
        for i in index:
            q.put(i)
            
    def job(self):
        """
        Initialisation.
        """
        num_proc = self.num_proc
        process_list = []
        index = np.arange(self._samples)
        q = Queue(len(index))
        counter1 = Value('i', 0)
        counter2 = Value('i', 0)
        #arr1 = Array('d', np.zeros(2*self._samples*self._num_params))
        #arr2 = Array('d', np.zeros(2*self._samples*self._num_params))
        arr1_base = Array(ctypes.c_double, 3*3*2)
        #shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
        #shared_array = shared_array.view(np.complex128).reshape(3, 3)
        self.qinit(q, index)
        for i in range(num_proc):
            p = Process(target=self.target,args=(q,arr1,arr2,counter1,counter2))
            process_list.append(p)
            p.start()
        for i in process_list:
            p.join() 
        print(process_list)
        print(p)
        
        print("getting arr")
        print(np.array(arr1),np.array(arr2))
        return np.array(arr1).reshape(self._samples,2*self._num_params),np.array(arr2).reshape(self._samples,2*self._num_params)
        
    
    
if __name__=="__main__":
    Num = 4
    qc = QuantumCircuit(Num)
    x = ParameterVector(r'$\theta$', length=8)
    [qc.h(i) for i in range(Num)]   
    [qc.ry(x[int(2*i)], i) for i in range(Num)]
    [qc.rz(x[int(2*i+1)], i) for i in range(Num)]
    qc.cx(0, range(1, Num))
    circ = qc
    job = Multiprocessing(circ=circ,descriptor="both")
    print(job.__dict__.keys())
    #job.job()
    
            
        