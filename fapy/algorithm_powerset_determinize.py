"""Implementation of the powerset determinization method

Given a finite automaton is a tuple :math:`\\mathcal{A} = ( A, Q,
Q_{\\mathrm{init}}, Q_{\\mathrm{acc}}, \\delta )`, this algorithm produces an
equivalent deterministic automaton :math:`\\mathcal{A}' = ( A, \\mathcal{P}
(Q), \\{ Q_{\\mathrm{init}} \\}, \\{ Q_{\\mathrm{acc}} \\}, \\gamma )`, where
for :math:`S \\in \\mathcal{P} (Q)` an :math:`\\epsilon`-closed subset of
states, and :math:`a \\in A` a letter, :math:`\\gamma (S, a)` is the
:math:`\\epsilon`-closure of all states reachable from :math:`S` by reading
:math:`a`.

See also:
    `Wikipedia page <https://en.wikipedia.org/wiki/Powerset_construction>`_
"""

from copy import (
    deepcopy
)
from typing import (
    Dict,
    List,
    Set,
    Tuple,
)

from fapy.common import (
    Letter,
    State
)
from fapy.finite_automaton import (
    FiniteAutomaton
)


def _state_identifier(state_set: Set[State]) -> str:
    """Convenience function that provides a name for a set of states

    Example::

        _state_identifier({'q1', 'q2'})

    return ``'q1,q2'``.
    """
    state_list = list(state_set)
    state_list.sort()
    return ",".join([str(state) for state in state_list])


def powerset_determinize(automaton: FiniteAutomaton) -> FiniteAutomaton:
    """Implementation of the powerset determinization method
    """

    initial_state_identifier = _state_identifier(automaton.initial_states)
    state_dict: Dict[str, Set[State]] = {
        initial_state_identifier: automaton.initial_states
    }

    unexplored_state_identifiers: List[str] = [initial_state_identifier]

    transitions: Dict[State, List[Tuple[Letter, State]]] = {}

    while unexplored_state_identifiers:
        state_identifier = unexplored_state_identifiers.pop(0)
        transitions[state_identifier] = []
        arrows: Dict[Letter, Set[State]] = {}
        for state in state_dict[state_identifier]:
            for letter, next_state in automaton.transitions[state]:
                if letter not in arrows:
                    arrows[letter] = set()
                arrows[letter].add(next_state)
        for letter in arrows:
            next_state_identifier = _state_identifier(arrows[letter])
            if next_state_identifier not in state_dict:
                state_dict[next_state_identifier] = arrows[letter]
                unexplored_state_identifiers.append(next_state_identifier)
            transitions[state_identifier].append(
                (letter, next_state_identifier)
            )

    states = set(state_dict.keys())
    accepting_states: Set[State] = set()
    for state_identifier in state_dict:
        if automaton.accepting_states.intersection(state_dict[state_identifier]):
            accepting_states.add(state_identifier)

    return FiniteAutomaton(
        alphabet=deepcopy(automaton.alphabet),
        states=states,
        initial_states=set([_state_identifier(automaton.initial_states)]),
        accepting_states=accepting_states,
        transitions=transitions
    )
