"""Finite automaton
"""

from typing import (
    Dict,
    List,
    Set,
    Tuple
)

Letter = str
Alphabet = Set[Letter]  # pylint: disable=invalid-name
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
            transitions: Dict[State, List[Tuple[Letter, State]]]):
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
            for letter, next_state in transitions[state]:
                if letter not in alphabet:
                    raise ValueError(
                        f'In transitions for state "{state}": '
                        f'unknown letter "{letter}"'
                    )
                if next_state not in states:
                    raise ValueError(
                        f'In transitions for state "{state}": '
                        f'unknown state "{next_state}"'
                    )

    def is_deterministic(self) -> bool:
        """Returns whether the automaton is deterministic or not.

        A automaton is deterministic if
        * it has a unique initial state,
        * the transition dictionary at any given state is a function.
        """
        if len(self._initial_states) != 1:
            return False
        for state in self._transitions:
            letters = [letter for letter, _ in self._transitions[state]]
            if len(letters) != len(set(letters)):
                return False
        return True
