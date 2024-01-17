from .DFA import DFA

from dataclasses import dataclass

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs
sink = frozenset({"sink"})
new_states_list = []

@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]
    initial_state = None
    visited = set()
    def epsilon_closure(self, state: STATE, visited = set()) -> set[STATE]:
        # compute the epsilon closure of a state (you will need this for subset construction)
        # see the EPSILON definition at the top of this file
        set_epsilon_closure = set()
        if not self.visited:
            self.initial_state = state
        if state not in self.visited:
            self.visited.add(state)
            set_epsilon_closure.add(state)
            if (state, EPSILON) in self.d:
                for i in self.d[(state, EPSILON)]:
                    set_epsilon_closure.update(self.epsilon_closure(i))
            if state == self.initial_state:
                 self.visited.clear()
        return set_epsilon_closure

    def create_new_members(self):
        instance = DFA(self.S, {frozenset(self.epsilon_closure(self.q0)), sink}, frozenset(self.epsilon_closure(self.q0)), {}, set())
        if self.F.intersection(instance.q0):
             instance.F.add(instance.q0)
        new_states_list.append(instance.q0)
        return instance


    def subset_construction(self) -> DFA[frozenset[STATE]]:
        new_instance = self.create_new_members()
        for big_states in new_states_list:
            for symbol in new_instance.S:
                new_instance.d[(sink, symbol)] = sink
                following_states = set()
                for state in big_states:
                    if (state, symbol) in self.d:
                        for tran in self.d[(state, symbol)]:
                            following_states.update(self.epsilon_closure(tran))
                if following_states:
                    new_instance.d[(big_states, symbol)] = frozenset(following_states)
                    if frozenset(following_states) not in new_states_list:
                        new_states_list.append(frozenset(following_states))
                        new_instance.K.add(frozenset(following_states))
                        if self.F.intersection(frozenset(following_states)):
                            new_instance.F.add(frozenset(following_states))
                else:
                    new_instance.d[(big_states, symbol)] = sink
        new_states_list.clear()
        return new_instance

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        self.F = {f(state) for state in self.F}
        self.K = {f(state) for state in self.K}
        self.q0 = f(self.q0)
        self.d = {(f(state), symbol): {f(next_state) for next_state in next_states} for (state, symbol), next_states in self.d.items()}

