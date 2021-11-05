import qiskit
import itertools
import typing
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import state_fidelity
from run import Simulation
from descriptors.expressibility import Expressibility
from descriptors.entanglement import Entanglement_Capability


class Analyser(Simulation,Expressibility,Entanglement_Capability):
    
    def __init__(self,descriptor:str='both',
                 circ=None,samples:int=10,method_ex:str='kl',
                 method_ec:str='mw',num_proc:int=1):
        
        Simulation.__init__(self,circ,samples,num_proc)
        self.theta_circuits, self.phi_circuits = self.get_circuits() 
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
        theta_circuits = self.theta_circuits
        phi_circuits = self.phi_circuits
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
        
    
    
if __name__=="__main__":
    Num = 4
    qc = QuantumCircuit(Num)
    x = ParameterVector(r'$\theta$', length=8)
    [qc.h(i) for i in range(Num)]   
    [qc.ry(x[int(2*i)], i) for i in range(Num)]
    [qc.rz(x[int(2*i+1)], i) for i in range(Num)]
    qc.cx(0, range(1, Num))
    circ = qc
    out = Analyser(circ=qc,samples=100,num_proc=2)
    print(out.__dict__.keys())
    print("params: ",out.thetas[0],out.phis[0])
    print(out.get_expressibility())
    print(out.get_entanglement())
    