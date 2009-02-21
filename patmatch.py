"""
patmatch.py -- Pattern matching module for Python.

This module gives python basic support for pattern matching
inspired by Haskell, O'Caml, and Scheme.

Author: Paul Butler     <paulgb@gmail.com>
Copyright (C) 2009

bzip license

VERSION 0.1

TODO:
 - readme file
 - license file
 - make cons reasonably fast
 - better inline docs
 - have a pattern that matches anything?
 - put the classes in a logical order, possibly in separate files
"""

class MatchExpression():
    """
    Dummy class which match expressions can extend.

    Subclasses of MatchExpression must implement one method:
    match(self, value, match_values_box)

    value is the value to be matched, match_values_box is a
    box to return a CapturedValues object to the original call
    to match.
    """
    pass


class MatchEq(MatchExpression):
    """
    Explicit equality match.

    Matches only if subject is equal to the given value.
    """
    
    def __init__(self, value):
        self.value = value


    def match(self, value, match_values_box, cap_val):
        return value == self.value

eq = MatchEq


class MatchOb(MatchExpression):
    def __init__(self, *args, **patterns):
        self.cls = None
        if args:
            self.cls = args[0]
        self.patterns = patterns
        

    def match(self, value, match_values_box, cap_val):
        for attr, pattern in self.patterns.iteritems():
            if not hasattr(value, attr):
                return False
            if not match_recur(pattern, getattr(value, attr), match_values_box, cap_val):
                return False
        return True
    
ob = MatchOb


class MatchDict(MatchExpression):
    def __init__(self, **patterns):
        self.patterns = patterns


    def match(self, value, match_values_box, cap_val):
        for attr, pattern in self.patterns.iteritems():
            if attr not in value:
                return False
            if not match_recur(pattern, value[attr], match_values_box, cap_val):
                return False
        return True

dt = MatchDict


class MatchType(MatchExpression):
    """
    Explicit type match.

    Matches only if the subject is an instance of the given type.
    """

    def __init__(self, type):
        self.type = type

    def match(self, value, match_values_box, cap_val):
        return isinstance(value, self.type)

type_is = MatchType


class MatchPredicate(MatchExpression):
    """
    Match based on a predicate function. Alias is pred().
    
    A value matches if and only if fun(value) is True.

    Examples:
    >>> match(pred(lambda x: x > 'bar'), 'baz')
    True
    >>> match(pred(lambda x: x > 'foo'), 'baz')
    False

    """
    def __init__(self, fun):
        self.fun = fun

    def match(self, value, match_values_box, cap_val):
        return self.fun(value)

pred = MatchPredicate


class MatchCons(MatchExpression):
    """
    Match a python list as if it were a cons cell. Alias is
    cons.

    A cons cell is a basic implementation of a linked list,
    where each element is stored as a (car, cdr) pair.
    car is the value of the element, and cdr is the next
    cons cell in the list.

    Eg. [1, 2, 3, 4] is (1, (2, (3, (4, []))))
    
    So cons(2, [3, 4, 5]) matches [2, 3, 4, 5]

    Note that the current implementation is not efficient,
    the list is copied many times. This should not yet be
    used on large lists.
    
    Examples:
    
    >>> match(cons(1, cons(2, [])), [1, 2])
    True

    """
    
    
    def __init__(self, car_pattern, cdr_pattern):
        self.car_pattern = car_pattern
        self.cdr_pattern = cdr_pattern
    
    def match(self, value, match_values_box, cap_val):
        if type(value) is not list:
            return False
        
        if match_recur(self.car_pattern, value[0], match_values_box, cap_val):
            return match_recur(self.cdr_pattern, value[1:], match_values_box, cap_val)

        return False

cons = MatchCons


class ValueBox(MatchExpression):
    """
    A match expression that will match any expression and store
    its value in a box. The box can be accessed later. This is
    the mechanism used for value capture.

    Examples:

    The ValueBox can be used directly:
    >>> a = ValueBox()
    >>> match(a, 8)
    True
    >>> a.get()
    8

    Or via an instance of CapturedValues:
    >>> mv = CapturedValues()
    >>> match(mv.a, 8) # mv.a is a ValueBox instance
    True
    >>> mv.a
    8
    
    """

    def __init__(self, name, match_values=None):
        self.name = name
        self.match_values = match_values

    def get(self):
        return self.value

    def match(self, value, match_values_box, cap_val):
        if len(match_values_box) != 0:
            pass
        elif self.match_values is not None:
            match_values_box.append(self.match_values)

        if self.name in cap_val:
            return cap_val[self.name] == value
        else:
            cap_val[self.name] = value
            return True

    def __repr__(self):
        return "<ValueBox: %s>" % repr(self.value)


class MatchAll(MatchExpression):
    """
    Match a value only if all of the given paterns
    are satisfied by the value. Alias is all().

    Examples:
    >>> match(all(int, pred(lambda x: x < 9)), 8)
    True
    >>> match(all(int, pred(lambda x: x < 9)), 10)
    False
    >>> match(all(int, pred(lambda x: x < 9)), "barney")
    False

    Also useful for testing a value before it is captured:
    >>> mv = CapturedValues()
    >>> match((all(int, mv.a), all(str, mv.b)), (4, "bingo"))
    True
    >>> mv.a
    4
    >>> mv.b
    'bingo'
    
    """

    def __init__(self, *patterns):
        self.patterns = patterns

    def match(self, value, match_values_box, cap_val):
        for pattern in self.patterns:
            if not match_recur(pattern, value, match_values_box, cap_val):
                return False
        return True

all = MatchAll


class MatchSome(MatchExpression):
    """
    Match a value if at least one of the given patterns
    is matched by the value.

    Examples:
    >>> match(some(int, str), 4)
    True
    >>> match(some(int, str), "foo")
    True
    >>> match(some(int, str), [])
    False

    """

    def __init__(self, *patterns):
        self.patterns = patterns
    
    def match(self, value, match_values_box, cap_val):
        for pattern in self.patterns:
            new_cap_val = dict(cap_val)
            if match_recur(pattern, value, match_values_box, new_cap_val):
                cap_val.update(new_cap_val)
                return True
        return False

some = MatchSome

class CapturedValues():
    """
    An object that creates ValueBoxes for capturing matched
    values.

    After a match is complete, the CapturedValues instance
    is switched into read mode, where it returns the values
    of the ValueBoxes instead of the boxes themselves.

    >>> cv = CapturedValues()
    >>> match(cv.a, 8)
    True
    >>> cv.a
    8
    
    """
    def __init__(self):
        self._clear()

    def __getattr__(self, name):
        if self._read_mode:
            return self._values[name]
        else:
            return ValueBox(name, self)

    def _close(self, values):
        self._values = values
        self._read_mode = True

    def _destroy(self):
        self._values = {}
        self._read_mode = True

    def _clear(self):
        self._values = None
        self._read_mode = False

    def __repr__(self):
        return "<CapturedValues>"

def match(pattern, subject):
    """
    Determine if the given subject matches the given pattern.

    May have additional side-effects such as capturing values
    from the subject.

    Examples:
    >>> match([1, int, (str, bool)], [1, 2, ("foo", False)])
    True
    >>> match([1, int, (str, bool)], [1, "bar", ("foo", False)])
    False

    """
    match_values_box = []
    cap_val = {}
    matched = match_recur(pattern, subject, match_values_box, cap_val)
    if len(match_values_box) != 0:
        if matched:
            match_values_box[0]._close(cap_val)
        else:
            match_values_box[0]._destroy()
    return matched


def match_recur(pattern, subject, match_values_box, cap_val):
    """
    Recursive match function. Shouldn't be called directly
    except from match.
    """

    if isinstance(pattern, MatchExpression):
        return pattern.match(subject, match_values_box, cap_val)
    
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
                    if not match_recur(p, s, match_values_box, cap_val):
                        return False
                return True
        else:
            return False

    return False

