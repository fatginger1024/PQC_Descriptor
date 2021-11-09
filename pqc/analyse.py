from pqc import Analyser
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector


def analyse(circ=None,samples:int=100,descriptor='both',method_ex:str='kl',
                 method_ec:str='mw',num_proc:int=1):
    """
    function that implements the package.
    -------------------------------------
    descriptor: 'ex','ec' or both, specifying the descriptor(s) one wants to use.
    circ: a qiskit QuantumCircuit object.
    samples: int, number of samples for the circuit parameters.
    method_ex: string, 'kl', or 'js', method for evaluating the circuit expressibility.
    method_ec: string, 'mw' or 'scott', method for evaluating the circuit entanglement capability.
    num_proc: int, number of processes for multiprocessing, the default is 1. 
    """
    
    analyser = Analyser(circ=circ,samples=samples,method_ex=method_ex,method_ec=method_ec,num_proc=num_proc)
    
    return analyser.get_expressibility(),analyser.get_entanglement()


if __name__=="__main__":
    Num = 4
    qc = QuantumCircuit(Num)
    x = ParameterVector(r'$\theta$', length=8)
    [qc.h(i) for i in range(Num)]   
    [qc.ry(x[int(2*i)], i) for i in range(Num)]
    [qc.rz(x[int(2*i+1)], i) for i in range(Num)]
    qc.cx(0, range(1, Num))
    circ = qc

    analyse(circ=qc)