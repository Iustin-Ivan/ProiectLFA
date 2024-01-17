from .NFA import NFA
small_letters = frozenset({"a", "b", "c", "d", "e", "f", "g", "h", "i", "j","k", "l", "m",
                           "n", "o", "p", "q", "r", "s", "t", "v", "u", "w", "x", "y", "z"})
big_letters = frozenset({"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
                         "O", "P", "Q", "R", "S", "T", "V", "U", "W", "X", "Y", "Z"})
numbers = frozenset({"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"})
reg_small = "[a-z]"
reg_big = "[A-Z]"
reg_num = "[0-9]"
operators_prio = {'|': 1, '&': 2, '*': 3, '+': 3, '?': 3, '(':-1, ')':-1}
characters = frozenset({"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "-" , ".", "\n", "\t", "_",
                        "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "v", "u", "w", "x", "y", "z",
                        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
                        "Q", "R", "S", "T", "V", "U", "W", "X", "Y", "Z", "0", "1", "2", "3", "4",
                        "5", "6", "7", "8", "9", " ", "@", ":", "/", "~", "`", "#", "$", "!", "%", "^"})
operators_b4_concat = frozenset({"*", "+", "?", ")"})
EPSILON = ''
# +=`, *=~, (=#, )=$
# smallletters = !, bigletters = %, numbers = ^
class Regex:
    string: str
    offset: int = 0

    def __init__(self, string: str):
        self.string = string
    def thompson(self) -> NFA[int]:
        nfa_stack = []
        postfix = self.string
        for c in postfix:
            if c == '*':
                nfa1 = nfa_stack.pop()
                initial, accept = self.offset, self.offset + 1
                self.offset += 2
                prev_final_state = nfa1.F.pop()
                nfa1.K.add(initial)
                nfa1.K.add(accept)
                nfa1.d[(initial, EPSILON)] = {nfa1.q0, accept}
                nfa1.d[(prev_final_state, EPSILON)] = {nfa1.q0, accept}
                nfa1.q0 = initial
                nfa1.F.add(accept)
                nfa_stack.append(nfa1)
            elif c == '&':
                nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
                prev_final_state = nfa1.F.pop()
                nfa1.d[(prev_final_state, EPSILON)] = {nfa2.q0}
                nfa1.F.add(nfa2.F.pop())
                nfa1.K.update(nfa2.K)
                nfa1.d.update(nfa2.d)
                nfa_stack.append(nfa1)
            elif c == '|':
                nfa2, nfa1 = nfa_stack.pop(), nfa_stack.pop()
                initial = self.offset
                nfa1.d[(initial, EPSILON)] = {nfa1.q0, nfa2.q0}
                accept = self.offset + 1
                self.offset += 2
                prev_final_state_1 = nfa1.F.pop()
                prev_final_state_2 = nfa2.F.pop()
                nfa1.d[(prev_final_state_1, EPSILON)] = {accept}
                nfa1.d[(prev_final_state_2, EPSILON)] = {accept}
                nfa1.K.add(initial)
                nfa1.K.add(accept)
                nfa1.q0 = initial
                nfa1.F.add(accept)
                nfa1.K.update(nfa2.K)
                nfa1.d.update(nfa2.d)
                nfa_stack.append(nfa1)
            elif c == '+':
                nfa1 = nfa_stack.pop()
                initial, accept = self.offset, self.offset+1
                self.offset += 2
                prev_final_state = nfa1.F.pop()
                nfa1.d[(prev_final_state, EPSILON)] = {nfa1.q0, accept}
                nfa1.d[(initial, EPSILON)] = {nfa1.q0}
                nfa1.q0 = initial
                nfa1.F.add(accept)
                nfa1.K.add(initial)
                nfa1.K.add(accept)
                nfa_stack.append(nfa1)
            elif c == '?':
                nfa1 = nfa_stack.pop()
                initial, accept = self.offset, self.offset+1
                self.offset += 2
                nfa1.K.update({initial, accept})
                prev_final_state = nfa1.F.pop()
                nfa1.d[(initial, EPSILON)] = {nfa1.q0, accept}
                nfa1.d[(prev_final_state, EPSILON)] = {accept}
                nfa1.q0 = initial
                nfa1.F.add(accept)
                nfa_stack.append(nfa1)
            else:
                initial, accept = self.offset, self.offset + 1
                self.offset += 2
                if c != "!" and c != "%" and c != "^":
                    if c == "`":
                        c = "+"
                    elif c == "~":
                        c = "*"
                    elif c == "#":
                        c = "("
                    elif c == "$":
                        c = ")"
                    nfa = NFA({c}, {initial, accept}, initial, {(initial, c): {accept}}, {accept})
                    # smallletters = !, bigletters = %, numbers = ^
                else:
                    transitions = dict()
                    if c == "!":
                        for i in small_letters:
                            transitions[(initial, i)] = {accept}
                    elif c == "%":
                        for i in big_letters:
                            transitions[(initial, i)] = {accept}
                    elif c == "^":
                        for i in numbers:
                            transitions[(initial, i)] = {accept}
                    nfa = NFA({c}, {initial, accept}, initial, transitions, {accept})
                nfa_stack.append(nfa)
        final_nfa = nfa_stack.pop()
        final_nfa.S.update(characters)
        final_nfa.S.update("(", ")", "+", "*")
        return final_nfa

# you should extend this class with the type constructors of regular expressions and overwrite the 'thompson' method
# with the specific nfa patterns. for example, parse_regex('ab').thompson() should return something like:

# >(0) --a--> (1) -epsilon-> (2) --b--> ((3))

# extra hint: you can implement each subtype of regex as a @dataclass extending Regex

def shunting_yard(infix, previous = None):

  postfix, op_stack, index = "", [], 0
  while index < len(infix):
    backlash = False
    char = infix[index]
    if char == ' ':
        index += 1
        continue
    if char == '(':
      if previous in characters or previous in operators_b4_concat:
        while op_stack and operators_prio[op_stack[-1]] >= operators_prio['&']:
            postfix += op_stack.pop()
        op_stack.append('&')
      op_stack.append(char)
    elif char == ')':
      while op_stack[-1] != '(':
        postfix += op_stack.pop()
      op_stack.pop()
    elif char in operators_prio:
      while op_stack and operators_prio[op_stack[-1]] >= operators_prio[char]:
        postfix += op_stack.pop()
      op_stack.append(char)
    elif char == "\\":
        if previous in characters or previous in operators_b4_concat:
            while op_stack and operators_prio[op_stack[-1]] >= operators_prio['&']:
                postfix += op_stack.pop()
            op_stack.append('&')
        next_char = infix[index+1]
        if next_char == "+":
            next_char = "`"
        elif next_char == "*":
            next_char = "~"
        elif next_char == "(":
            next_char = "#"
        elif next_char == ")":
            next_char = "$"
        postfix = postfix + next_char
        index += 2
        previous = next_char
        backlash = True

    else:
      if previous in characters or previous in operators_b4_concat:
          while op_stack and operators_prio[op_stack[-1]] >= operators_prio['&']:
            postfix += op_stack.pop()
          op_stack.append('&')
      postfix = postfix + char

    if not backlash:
        index += 1
        if char != ' ':
            previous = char



  while op_stack:
    postfix += op_stack.pop()

  return postfix

def replace_syntactic_sugars(input_string):
    # smallletters = !, bigletters = %, numbers = ^
    result_string = input_string.replace(reg_big, "%")
    result_string = result_string.replace(reg_small, "!")
    result_string = result_string.replace(reg_num, "^")
    return result_string



def parse_regex(regex: str) -> Regex:
    # create a Regex object by parsing the string
    new_string = replace_syntactic_sugars(regex)
    processed_string = shunting_yard(new_string)
    rex = Regex(processed_string)
    return rex
