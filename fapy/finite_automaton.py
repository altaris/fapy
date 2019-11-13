"""Finite automaton
"""

from copy import (
    deepcopy
)
from typing import (
    Dict,
    List,
    Set,
    Tuple
)

from graphviz import (
    Digraph
)

from fapy.common import *


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
        self.alphabet = alphabet
        self.states = states
        self.initial_states = initial_states
        self.accepting_states = accepting_states
        self.transitions = transitions
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
                alphabet_plus_epsilon = list(alphabet) + ['ε']
                if letter not in alphabet_plus_epsilon:
                    raise ValueError(
                        f'In transitions for state "{state}": '
                        f'unknown letter "{letter}"'
                    )
                if next_state not in states:
                    raise ValueError(
                        f'In transitions for state "{state}": '
                        f'unknown state "{next_state}"'
                    )

    def draw(self, **kwargs) -> Digraph:
        """Renders the automaton using graphviz
        """
        graph = Digraph(**kwargs)
        graph.node('', shape='point')
        for state in self.states:
            if state in self.accepting_states:
                graph.node(str(state), shape='doublecircle')
            else:
                graph.node(str(state), shape='circle')
            if state in self.initial_states:
                graph.edge('', str(state))
        for state in self.transitions:
            arrows = {}  # type: Dict[State, List[Letter]]
            for letter, next_state in self.transitions.get(state, []):
                arrows[next_state] = arrows.get(next_state, []) + [letter]
            for next_state in arrows:
                arrows[next_state].sort()
                label = ", ".join(arrows[next_state])
                graph.edge(str(state), str(next_state), label=label)
        return graph

    def epsilon_closure(self, states: Set[State]) -> Set[State]:
        """Computes the epsilon closure of a set of states
        """
        states_closed = deepcopy(states)
        unexplored_states = list(states)
        while unexplored_states:
            unexplored_state = unexplored_states.pop(0)
            for letter, next_state in \
                self.transitions.get(unexplored_state, []):
                if letter == 'ε' and next_state not in states_closed:
                    states_closed.add(next_state)
                    unexplored_states.append(next_state)
        return states_closed

    def is_deterministic(self) -> bool:
        """Returns whether the automaton is deterministic or not.

        A automaton is deterministic if
        * it has a unique initial state,
        * the transition dictionary at any given state is a function.
        """
        if len(self.initial_states) != 1:
            return False
        for state in self.transitions:
            letters = [letter for letter, _ in self.transitions[state]]
            if len(letters) != len(set(letters)):
                return False
            if 'ε' in letters:
                return False
        return True

    def read(self, word: Word) -> bool:
        """Reads a word and returns whether the automaton accepts it or not.
        """
        if not set(word).issubset(self.alphabet):
            raise ValueError(f'Invalid word {word}')
        current_states = self.epsilon_closure(self.initial_states)
        for letter in word:
            new_states = set()
            for state in current_states:
                for l, q in self.transitions.get(state, []):
                    if letter == l:
                        new_states.add(q)
            current_states = self.epsilon_closure(new_states)
        return bool(self.accepting_states.intersection(current_states))
