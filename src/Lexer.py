from src.Regex import Regex
from src.Regex import parse_regex
from src.NFA import NFA
from src.DFA import DFA
EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs
sink = frozenset({"sink"})
class Lexer:
    dfa = DFA(set(), set(), "", {}, set())
    token_list = []
    final_nfa = None
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # initialisation should convert the specification to a dfa which will be used in the lex method
        # the specification is a list of pairs (TOKEN_NAME:REGEX)
        regex_list = [parse_regex(pair[1]) for pair in spec]
        nfa_list = [reg.thompson() for reg in regex_list]
        for i in range(len(nfa_list)):
            nfa_list[i].remap_states(lambda x: spec[i][0] + " " + str(x))
        final_nfa = NFA(nfa_list[0].S, set(), "INIT", {}, set())
        final_nfa.d[("INIT", EPSILON)] = {nfa_list[0].q0}
        final_nfa.K.add("INIT")
        for i in range(len(nfa_list)):
            final_nfa.K.update(nfa_list[i].K)
            final_nfa.d.update(nfa_list[i].d)
            final_nfa.F.update(nfa_list[i].F)
            final_nfa.d[("INIT", EPSILON)].add(nfa_list[i].q0)
        self.dfa = final_nfa.subset_construction()
        self.token_list = spec
        self.final_nfa = final_nfa

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # this method splits the lexer into tokens based on the specification and the rules described in the lecture
        # the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)
        # if an error occurs and the lexing fails, you should return none # todo: maybe add error messages as a task
        consumed = 0
        max_len = 0
        i = 0
        curr_token = None
        tok_list = []
        to_be_added = False
        count, pos = count_and_positions(word, "\n")
        intermediary_state = False
        while i <= len(word):
            self.dfa.accept(word[consumed:i])
            if self.dfa.current_state == sink:
                intermediary_state = False
                consumed += max_len
                i = consumed + 1
                if curr_token is not None:
                    tok_list.append(curr_token)
                    to_be_added = False
                    curr_token = None
                else:
                    line = 0
                    curr_pos = 0
                    for j in range(len(pos)):
                        if j < i:
                            line += 1
                            curr_pos = pos[j]
                        else:
                            break
                    final_pos = i - curr_pos
                    if i == 1 or i == len(word):
                        final_pos -= 1
                    if line:
                        final_pos -= 1
                    return [("", "No viable alternative at character " + str(final_pos) + ", line " + str(line))]
                max_len = 0
            else:
                if self.dfa.current_state in self.dfa.F:
                    intermediary_state = False
                    to_be_added = True
                    for token in self.token_list:
                        found = False
                        for elem in self.dfa.current_state:
                            words = elem.split()
                            if words[0] == token[0] and elem in self.final_nfa.F:
                                curr_token = (token[0], word[consumed:i])
                                max_len = i - consumed
                                i += 1
                                found = True
                                break
                        if found:
                            break
                else:
                    i += 1
                    intermediary_state = True

        if to_be_added:
            tok_list.append(curr_token)
            curr_token = None
        if intermediary_state:
            return [("", "No viable alternative at character EOF" + ", line " + str(count))]
        return tok_list

def count_and_positions(s, char):
    count = 0
    positions = []

    for i, c in enumerate(s):
        if c == char:
            count += 1
            positions.append(i)

    return count, positions
