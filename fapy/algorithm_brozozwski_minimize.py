"""Implements Brozozwski's minimization algoithm

See also:
    `Wikipedia page <https://en.wikipedia.org/wiki/DFA_minimization#Brzozowski's_algorithm>`_
"""

from typing import (
    Dict,
    List,
    Tuple
)

from fapy.common import (
    Letter,
    State
)
from fapy.finite_automaton import (
    FiniteAutomaton
)
from fapy.algorithm_powerset_determinize import (
    powerset_determinize
)


def brozozwski_minimize(automaton: FiniteAutomaton) -> FiniteAutomaton:
    """Implements Brozozwski's minimization algoithm
    """
    return powerset_determinize(transpose(
        powerset_determinize(transpose(
            powerset_determinize(automaton)
        ))
    ))


def transpose(automaton: FiniteAutomaton) -> FiniteAutomaton:
    """Transposes a finite automaton

    Let :math:`\\mathcal{A} = ( A, Q, Q_{\\mathrm{init}}, Q_{\\mathrm{acc}},
    \\delta )` be a finite automaton. Its **transpose** :math:`\\mathcal{A}^t`
    is given by :math:`\\mathcal{A}^t = ( A, Q, Q_{\\mathrm{acc}},
    Q_{\\mathrm{init}}, \\delta^t )` (note that initial and accepting states
    have been swaped), where for :math:`a \\in A` and :math:`q \\in Q`,
    :math:`\\delta^t (q, a) = \\{ r \\in Q \\mid \\delta (r, a) = q \\}`.
    """
    transposed_transitions: Dict[State, List[Tuple[Letter, State]]] = {}
    for state in automaton.states:
        transposed_transitions[state] = []
    for state_left in automaton.transitions:
        for letter, state_right in automaton.transitions[state_left]:
            transposed_transitions[state_right].append((letter, state_left))

    return FiniteAutomaton(
        alphabet=automaton.alphabet,
        states=automaton.states,
        initial_states=automaton.accepting_states,
        accepting_states=automaton.initial_states,
        transitions=transposed_transitions
    )
