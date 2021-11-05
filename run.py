import qiskit
import typing
from interface import Interface

class run_simulator(Interface):
    
    def __init__(self,circ=None,samples:int=1000):
        Interface.__init__(self,circ,samples)
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
    
        
        