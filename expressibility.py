import typing
import qiskit
import itertools
import numpy as np
from qiskit.circuit.library import TwoLocal
from qiskit.quantum_info import state_fidelity
from scipy.spatial.distance import jensenshannon


class Expressibility:
    
    def __init__(self,circ=None,samples=1000):
        self.circ = circ
        self.samples = samples
        self.num_qubits = circ.num_qubits
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
    def kl_divergence(prob_a: np.ndarray, prob_b: np.ndarray) -> float:
        """Returns KL divergence between two probabilities"""
        prob_a[prob_a == 0] = 1e-10
        kl_div = np.sum(np.where(prob_a != 0, prob_a * np.log(prob_a / prob_b), 0))
        return typing.cast(float, kl_div)
    

    def prob_haar(self) -> np.ndarray:
        """Returns probability density function of fidelities for Haar Random States"""
        fidelity = np.linspace(0, 1, self.samples)
        num_qubits = self.num_qubits
        
        return (2 ** num_qubits - 1) * (1 - fidelity + 1e-8) ** (2 ** num_qubits - 2)

    def prob_pqc(self, shots: int = 1024) -> np.ndarray:
        """Return probability density function of fidelities for PQC
        :param shots: number of shots for circuit execution
        :returns fidelities (np.array): np.array of fidelities
        """
        thetas, phis = self.params

        theta_circuits = [
                self.simulate(theta)
                for theta in thetas
        ]
            
        phi_circuits = [
            self.simulate(phi)
            for phi in phis
        ]
        fidelity = np.array(
            [
                state_fidelity(rho_a, rho_b)
                for rho_a, rho_b in itertools.product(theta_circuits, phi_circuits)
            ]
        )
        
        return np.array(fidelity)
    
    def simulate(self,theta):
        circuit =  self.circ.assign_parameters(theta)
        circuit.snapshot("final", snapshot_type="statevector")
        result = qiskit.execute(
            circuit, qiskit.Aer.get_backend("aer_simulator_statevector")
        ).result()
        result_data = result.data(0)["snapshots"]["statevector"]["final"][0]

        return result_data
    
    
    def get_result(self, measure: str = "kld", shots: int = 1024) -> float:
        
        r"""Returns expressibility for the circuit
        .. math::
            Expr = D_{KL}(\hat{P}_{PQC}(F; \theta) | P_{Haar}(F))\\
            Expr = D_{\sqrt{JSD}}(\hat{P}_{PQC}(F; \theta) | P_{Haar}(F))
        :param measure: specification for the measure used in the expressibility calculation
        :param shots: number of shots for circuit execution
        :returns pqc_expressibility: float, expressibility value
        :raises ValueError: if invalid measure is specified
        """
        haar = self.prob_haar()
        haar_prob: np.ndarray = haar / float(haar.sum())

        if len(self.circ.parameters) > 0:
            fidelity = self.prob_pqc(shots)
        else:
            fidelity = np.ones(self.samples ** 2)

        bin_edges: np.ndarray
        pqc_hist, bin_edges = np.histogram(
            fidelity, self.samples, range=(0, 1), density=True
        )
        pqc_prob: np.ndarray = pqc_hist / float(pqc_hist.sum())

        if measure == "kld":
            pqc_expressibility = self.kl_divergence(pqc_prob, haar_prob)
        elif measure == "jsd":
            pqc_expressibility = jensenshannon(pqc_prob, haar_prob, 2.0)
        else:
            raise ValueError("Invalid measure provided, choose from 'kld' or 'jsd'")
        self.plot_data = [haar_prob, pqc_prob, bin_edges]
        self.expr = pqc_expressibility

        return pqc_expressibility

if __name__=="__main__":
    qc = TwoLocal(3, 'ry', 'cx', 'linear', reps=2, insert_barriers=True)
    measure = Expressibility(circ=qc)
    e = measure.get_result()
    print("Expressibility is: ",e)