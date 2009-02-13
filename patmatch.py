

class MatchExpression():
    pass


class ValueBox(MatchExpression):
    def __init__(self, box):
        self.value = None
        self.box = box

    def get(self):
        return self.value

    def match(self, value, match_values_box):
        if len(match_values_box) != 0:
            assert match_values_box[0] is self.box
        else:
            #self.box._clear()
            match_values_box.append(self.box)
        self.value = value
        print self.value
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
        print name, self._read_mode, [(a, b.get()) for a, b in self._values.iteritems()]
        if self._read_mode:
            return self._values[name].get()
        else:
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

