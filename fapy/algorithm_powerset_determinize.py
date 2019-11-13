"""Determinizes an automaton using the powerset method
"""

from copy import (
    deepcopy
)
from typing import (
    Dict,
    List,
    Set,
    Tuple,
    Union
)

from fapy.common import (
    Letter,
    State
)
from fapy.finite_automaton import (
    FiniteAutomaton
)


def _state_identifier(state_set: Set[State]) -> str:
    state_list = list(state_set)
    state_list.sort()
    return ",".join([str(state) for state in state_list])


def powerset_determinize(automaton: FiniteAutomaton) -> FiniteAutomaton:

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
