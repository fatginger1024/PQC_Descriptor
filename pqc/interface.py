# -*- coding: utf-8 -*-

class Interface:
    
    def __init__(self,circ=None,samples:int=1000)->None:
        """
        Interface which initialise the user input.
        ------------------------------------------
        circ: qiskit.QuantumCircuit, a user defined quantum circuit, must contain parametrised quantum gates
        samples: int, number of samples we want to draw for the parameters.
        """
        self._circ = circ 
        self._num_qubits = circ.num_qubits
        self._samples = samples
        self._num_params = circ.num_parameters
        