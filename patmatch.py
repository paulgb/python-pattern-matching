
class MatchExpression():
    pass


class MatchPredicate(MatchExpression):
    def __init__(self, fun):
        self.fun = fun

    def match(self, value, match_values_box):
        return self.fun(value)

pred = MatchPredicate


class MatchCons(MatchExpression):
    # TODO: make cons efficient
    
    def __init__(self, car_pattern, cdr_pattern):
        self.car_pattern = car_pattern
        self.cdr_pattern = cdr_pattern
    
    def match(self, value, match_values_box):
        if type(value) is not list:
            return False
        
        if match_recur(self.car_pattern, value[0], match_values_box):
            return match_recur(self.cdr_pattern, value[1:], match_values_box)

        return False

cons = MatchCons


class ValueBox(MatchExpression):
    def __init__(self, match_values):
        self.value = None
        self.match_values = match_values

    def get(self):
        return self.value

    def match(self, value, match_values_box):
        if len(match_values_box) != 0:
            assert match_values_box[0] is self.match_values
        else:
            match_values_box.append(self.match_values)
        self.value = value
        return True


class MatchAll(MatchExpression):
    def __init__(self, *patterns):
        self.patterns = patterns

    def match(self, value, match_values_box):
        for pattern in self.patterns:
            if not match_recur(pattern, value, match_values_box):
                return False
        return True

all = MatchAll


class MatchSome(MatchExpression):
    def __init__(self, *patterns):
        self.patterns = patterns
    
    def match(self, value, match_values_box):
        for pattern in self.patterns:
            if match_recur(pattern, value, match_values_box):
                return True
        return False

some = MatchSome


class MatchValues():
    def __init__(self):
        self._clear()

    def __getattr__(self, name):
        if self._read_mode:
            return self._values[name].get()
        else:
            if name not in self._values:
                self._values[name] = ValueBox(self)
            return self._values[name]

    def _close(self):
        self._read_mode = True

    def _destroy(self):
        # TODO: set a flag here and raise an better exception when __getattr__ is called
        self._values = {}
        self._read_mode = True

    def _clear(self):
        self._values = {}
        self._read_mode = False


def match(pattern, subject):
    match_values_box = []
    matched = match_recur(pattern, subject, match_values_box)
    if len(match_values_box) != 0:
        if matched:
            match_values_box[0]._close()
        else:
            match_values_box[0]._destroy()
    return matched


def match_recur(pattern, subject, match_values_box):
    if isinstance(pattern, MatchExpression):
        return pattern.match(subject, match_values_box)
    
    if pattern == subject:
        return True

    if type(pattern) is type:
        return type(subject) is pattern

    if type(pattern) in [list, tuple]:
        if type(subject) is type(pattern):
            if len(pattern) != len(subject):
                return False
            else:
                for p, s in zip(pattern, subject):
                    if not match_recur(p, s, match_values_box):
                        return False
                return True
        else:
            return False

    return False

