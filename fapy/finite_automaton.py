"""Finite automaton
"""

from typing import (
    Dict,
    Set
)

Alphabet = Set[Letter]  # pylint: disable=invalid-name
Letter = str
State = str


class FiniteAutomaton:
    """Finite automaton
    """

    # pylint: disable=too-many-arguments
    def __init__(
            self,
            alphabet: Alphabet,
            states: Set[State],
            initial_states: Set[State],
            accepting_states: Set[State],
            transitions: Dict[State, Dict[Letter, State]]):
        self._alphabet = alphabet
        self._states = states
        self._initial_states = initial_states
        self._accepting_states = accepting_states
        self._transitions = transitions
        if not initial_states:
            raise ValueError('An automaton must have at least 1 initial state')
        if not initial_states.issubset(states):
            raise ValueError('initial_states ⊈ states')
        if not accepting_states.issubset(states):
            raise ValueError('accepting_states ⊈ states')
        for state in transitions:
            if state not in states:
                raise ValueError(f'Unknown state "{state}" in transitions')
            for letter in transitions[state]:
                if letter not in alphabet:
                    raise ValueError(
                        f'In transitions for state "{state}": '
                        f'unknown letter "{letter}"'
                    )
                if transitions[state][letter] not in states:
                    raise ValueError(
                        f'In transitions for state "{state}": '
                        f'unknown state "{transitions[state][letter]}"'
                    )
