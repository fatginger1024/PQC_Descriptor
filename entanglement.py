import typing
import qiskit
import itertools
import numpy as np
from qiskit.quantum_info import partial_trace
from qiskit.circuit.library import TwoLocal



class Entanglement_Capability:
    
    def __init__(self,circ=None,method='mw',samples=10):
        """
        circ: qiskit QuantumCircuit
        method: string, "kl" or "js"
        samples: number of evaluations of circuits
        """
        self.circ = circ
        self.num_qubits = circ.num_qubits
        self.samples = samples
        self.method = method
        self.params = self.get_params()
        
        
    def get_params(self) -> typing.Tuple[typing.List, typing.List]:
        """Generate parameters for the calculation of expressibility
        :returns theta (np.array): first list of parameters for the parameterized quantum circuit
        :returns phi (np.array): second list of parameters for the parameterized quantum circuit
        """
        
        theta = [
            {p: 2 * np.random.random() * np.pi for p in self.circ.parameters}
            for _ in range(self.samples)
        ]
        phi = [
            {p: 2 * np.random.random() * np.pi for p in self.circ.parameters}
            for _ in range(self.samples)
        ]
        
        params = theta,phi
        
        return params

    @staticmethod
    def scott_helper(state, perms):
        
        dems = np.linalg.matrix_power(
            [partial_trace(state, list(qb)).data for qb in perms], 2
        )
        trace = np.trace(dems, axis1=1, axis2=2)
        return np.sum(trace).real

    def meyer_wallach_measure(self,states, num_qubits):
        r"""Returns the meyer-wallach entanglement measure for the given circuit.
        .. math::
            Q = \frac{2}{|\vec{\theta}|}\sum_{\theta_{i}\in \vec{\theta}}
            \Bigg(1-\frac{1}{n}\sum_{k=1}^{n}Tr(\rho_{k}^{2}(\theta_{i}))\Bigg)
        """
        num_qubits = self.num_qubits
        permutations = list(itertools.combinations(range(num_qubits), num_qubits - 1))
        ns = 2 * sum(
            [
                1 - 1 / num_qubits * self.scott_helper(state, permutations)
                for state in states
            ]
        )
        
        return ns.real
 
    def scott_measure(self,states, num_qubits):
        r"""Returns the scott entanglement measure for the given circuit.
        .. math::
            Q_{m} = \frac{2^{m}}{(2^{m}-1) |\vec{\theta}|}\sum_{\theta_i \in \vec{\theta}}\
            \bigg(1 - \frac{m! (n-m)!)}{n!}\sum_{|S|=m} \text{Tr} (\rho_{S}^2 (\theta_i)) \bigg)\
            \quad m= 1, \ldots, \lfloor n/2 \rfloor
        """
        num_qubits = self.num_qubits
        m = range(1, num_qubits // 2 + 1)
        permutations = [
            list(itertools.combinations(range(num_qubits), num_qubits - idx))
            for idx in m
        ]
        combinations = [1 / comb(num_qubits, idx) for idx in m]
        contributions = [2 ** idx / (2 ** idx - 1) for idx in m]
        ns = []

        for ind, perm in enumerate(permutations):
            ns.append(
                contributions[ind]
                * sum(
                    [
                        1 - combinations[ind] * self.scott_helper(state, perm)
                        for state in states
                    ]
                )
            )

        return np.array(ns)
    
  
    def simulate(self,theta):
        circuit =  self.circ.assign_parameters(theta)
        circuit.snapshot("final", snapshot_type="statevector")
        result = qiskit.execute(
            circuit, qiskit.Aer.get_backend("aer_simulator_statevector")
        ).result()
        result_data = result.data(0)["snapshots"]["statevector"]["final"][0]

        return result_data
    
    
    def get_result(self):
        num_qubits = self.num_qubits
        thetas, phis = self.params
        method = self.method
        if method=='mw':
            
            theta_circuits = [
                self.simulate(theta)
                for theta in thetas
                    ]
            
            phi_circuits = [
                self.simulate(phi)
                for phi in phis
            ]
            
            circ_entanglement_capability = self.meyer_wallach_measure(
                        theta_circuits + phi_circuits, num_qubits
                    ) / (2 * self.samples)
            
        elif method=='scott':
            theta_circuits = [
            self.simulate(theta)
            for theta in thetas
                ]
            phi_circuits = [
                self.simulate(phi)
                for phi in phis
            ]
            circ_entanglement_capability = self.scott_measure(
                        theta_circuits + phi_circuits, num_qubits
                    ) / (2 * self.samples)
            
        else:
            raise ValueError("Invalid measure provided, choose from 'mw' or 'scott'")
            
        return circ_entanglement_capability
    
    
if __name__=="__main__":
    qc = TwoLocal(3, 'ry', 'cx', 'linear', reps=2, insert_barriers=True)
    measure = Entanglement_Capability(qc,samples=10)
    a = measure.get_result()
    print("entanglement capability is: ",a)