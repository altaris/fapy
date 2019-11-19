"""This module implements a representation of finite automata

A finite automaton is a tuple :math:`\\mathcal{A} = ( A, Q, Q_{\\mathrm{init}},
Q_{\\mathrm{acc}}, \\delta )`, where

* :math:`A` is a set of *letters*, called the *alphabet*;
* :math:`Q` is a finite set of *states*;
* :math:`Q_{\\mathrm{init}} \\subseteq  Q` is the set of *initial states*;
* :math:`Q_{\\mathrm{acc}} \\subseteq Q` is the set of *accepting states*;
* :math:`\\delta : Q \\times A \\rightarrow \\mathcal{P} (Q)` is the
  *transition function*, where :math:`\\mathcal{P} (Q)` is the powerset of
  :math:`Q`.

In `fapy`, finite automata are constructed by specifying those parameters in
that order::

    automaton = FiniteAutomaton(
        alphabet={'a', 'b'},
        states={'q0', 'q1'},
        initial_states={'q0'},
        accepting_states={'q1'},
        transitions={
            'q0': [('a', 'q0'), ('b', 'q0'), ('a', 'q1')],
            'q1': [('a', 'q1'), ('b', 'q1')]
        }
    )

This example constructs an automaton over the alphabet :math:`\\{ a, b \\}`
whose langage consists in all words containing the letter :math:`a`.

:Note on determinism: In `fapy`, automata are non deterministic. Being
  deterministic is a *property* that can be retrieved using
  :meth:`FiniteAutomaton.is_deterministic`.
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

from graphviz import (
    Digraph
)

from fapy.common import (
    Alphabet,
    Letter,
    State,
    Word
)


class FiniteAutomaton:
    """Finite automaton
    """

    def __add__(self, other) -> 'FiniteAutomaton':
        """Returns the disjoint union of two automata

        If :math:`\\mathcal{A} = ( A, Q, Q_{\\mathrm{init}}, Q_{\\mathrm{acc}},
        \\delta )` and :math:`\\mathcal{A}' = ( A', Q', Q'_{\\mathrm{init}},
        Q'_{\\mathrm{acc}}, \\delta' )`, then :math:`\\mathcal{A} + \\mathcal{A}' =
        ( A \\cup A', Q + Q', Q_{\\mathrm{init}} + Q'_{\\mathrm{init}},
        Q_{\\mathrm{acc}} + Q'_{\\mathrm{acc}}, \\delta + \\delta' )`.

        If :math:`\\mathcal{L} (\\mathcal{A})` is the langage recognized by
        :math:`\\mathcal{A}`, then :math:`\\mathcal{L} (\\mathcal{A} +
        \\mathcal{A}') = \\mathcal{L} (\\mathcal{A}) \\cup \\mathcal{L}
        (\\mathcal{A}')`.
        """
        if not isinstance(other, FiniteAutomaton):
            raise NotImplementedError
        return FiniteAutomaton(
            alphabet=self.alphabet | other.alphabet,
            states=self.states | other.states,
            initial_states=self.initial_states | other.initial_states,
            accepting_states=self.accepting_states | other.accepting_states,
            transitions={**self.transitions, **other.transitions}
        )

    def __mul__(self, other) -> 'FiniteAutomaton':
        """Returns the concatenation of two automata

        If :math:`\\mathcal{A} = ( A, Q, Q_{\\mathrm{init}}, Q_{\\mathrm{acc}},
        \\delta )` and :math:`\\mathcal{A}' = ( A', Q', Q'_{\\mathrm{init}},
        Q'_{\\mathrm{acc}}, \\delta' )`, then :math:`\\mathcal{A} \\cdot
        \\mathcal{A}' = ( A \\cup A', Q + Q', Q_{\\mathrm{init}},
        Q'_{\\mathrm{acc}}, \\delta'')`, where :math:`\\delta''` is
        :math:`\\delta + \\delta'` with the additional
        :math:`\\epsilon`-transitions from all accepting states of
        :math:`\\mathcal{A}` to all initial sates of :math:`\\mathcal{A}'`.

        If :math:`\\mathcal{L} (\\mathcal{A})` is the langage recognized by
        :math:`\\mathcal{A}`, then :math:`\\mathcal{L} (\\mathcal{A}
        + \\mathcal{A}') = \\mathcal{L} (\\mathcal{A}) \\cdot \\mathcal{L}
        (\\mathcal{A}')`.
        """
        if not isinstance(other, FiniteAutomaton):
            raise NotImplementedError
        result = FiniteAutomaton(
            alphabet=self.alphabet | other.alphabet,
            states=self.states | other.states,
            initial_states=self.initial_states,
            accepting_states=other.accepting_states,
            transitions={
                **self.transitions,
                **other.transitions
            }
        )
        for q_acc_left in self.accepting_states:
            if q_acc_left not in result.transitions:
                result.transitions[q_acc_left] = []
            for q_init_right in other.initial_states:
                result.transitions[q_acc_left].append(('ε', q_init_right))
        return result


    # pylint: disable=too-many-arguments
    def __init__(
            self,
            alphabet: Alphabet,
            states: Set[State],
            initial_states: Set[State],
            accepting_states: Set[State],
            transitions: Dict[State, List[Tuple[Letter, State]]]):
        """Constructor

        Args:
            alphabet: The alphabet of the automaton
            states: The set of states
            initial_states: The subset of initial states
            accepting_states: The subset of accepting states
            transitions: The transition function, represented as a
                ``Dict[State, List[Tuple[Letter, State]]]``

        Raises:
            ValueError: If the parameters are invalid, e.g. the set of
                accepting states is not a subset of the set of states. The text
                of the exception should provide an explanation.

        """

        self.alphabet = alphabet
        self.states = states
        self.initial_states = initial_states
        self.accepting_states = accepting_states
        self.transitions = transitions

        # Parameters validation
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

        Returns:
            A :class:`graphviz.Digraph` object.

        See also:
            `graphviz documentation <https://graphviz.readthedocs.io/en/stable/>`_
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
        """Computes the :math:`\\epsilon`-closure of a set of states

        If :math:`S \\subseteq Q` is a set of states, then its
        :math:`\\epsilon`-*closure* if the set of states reachable from any
        state of :math:`S` using :math:`0` or more
        :math:`\\epsilon`-transitions.
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
        """Returns whether the automaton is deterministic or not

        A automaton is deterministic if

        * it has a unique initial state,
        * its transition function :math:`\\delta` is a function :math:`Q \\times
          A \\rightarrow Q`, instead of just :math:`\\delta : Q \\times A
          \\rightarrow \\mathcal{P} (Q)`.
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

    def read(self, word: Union[str, Word]) -> bool:
        """Reads a word and returns whether the automaton accepts it or not
        """
        if isinstance(word, str):
            word = list(word)
        current_states = self.epsilon_closure(self.initial_states)
        for letter in word:
            new_states = set()
            for state in current_states:
                for arrow_letter, next_state in self.transitions.get(state, []):
                    if letter == arrow_letter:
                        new_states.add(next_state)
            current_states = self.epsilon_closure(new_states)
        return bool(self.accepting_states.intersection(current_states))


def empty_word_automaton(state: State = 'q0') -> FiniteAutomaton:
    """Returns the automaton with a unique state that is both initial and
    accepting

    Args:
        state: The name of the unique state. Defaults to ``q0``.
    """
    return FiniteAutomaton(
        alphabet=set(),
        states={state},
        initial_states={state},
        accepting_states={state},
        transitions=dict()
    )


def letter_automaton(
        letter: Letter,
        initial_state: State = 'q0',
        accepting_state: State = 'q1') -> FiniteAutomaton:
    """Returns a 2 states automaton that only accepts the given letter



    Args:
        letter: The letter in question. It can be :math:`\\epsilon` (even if
            structly speaking, it is not a letter).
        initial_state: The name of the initial state. Defaults to ``q0``.
        accepting_state: The name of the accepting state. Defaults to ``q1``.
    """
    return FiniteAutomaton(
        alphabet={letter},
        states={initial_state, accepting_state},
        initial_states={initial_state},
        accepting_states={accepting_state},
        transitions={initial_state: [(letter, accepting_state)]}
    )
