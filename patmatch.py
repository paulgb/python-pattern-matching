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
 - make into a python module
"""

## Main match() method

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

    if isinstance(pattern, MatchPattern):
        return pattern.match(subject, match_values_box, cap_val)
    
    if pattern == subject:
        return True

    if isinstance(pattern, type):
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


## Match Patterns

class MatchPattern():
    """
    Dummy class which match patterns can extend.

    Subclasses of MatchPattern must implement one method:
    match(self, value, match_values_box, cap_val)

    value is the value to be matched
    match_values_box is a box to return a CapturedValues object
      to the original call to match.
    cap_val is a dict for the values captured so far in the match.
    """
    pass



class MatchEq(MatchPattern):
    """
    Explicit equality match. Alias is `eq`.

    Matches only if subject is equal to the given value.

    Examples:
    >>> match(eq(5), 5)
    True
    >>> match(eq(int), 5)
    False
    """
    
    def __init__(self, value):
        self.value = value


    def match(self, value, match_values_box, cap_val):
        return value == self.value


eq = MatchEq



class MatchOb(MatchPattern):
    """
    Match an object, optionally matching attributes of that
    object. Alias is `ob`.

    Constructor takes one optional paramater (the class of the object to be
    matched), followed by as many named paramaters as are neccesary.

    The values of the named paramaters should be patterns accepted by match().
    The attributes of the object will be checked against the patterns given by
    the same name.

    Examples:
    >>> class Animal:
    ...     legs = None
    ...     habitat = None
    >>> fish = Animal()
    >>> fish.habitat = 'water'
    >>> fish.legs = 0
    >>> match(ob(Animal), fish)
    True
    >>> match(ob(Animal, legs=0), fish)
    True
    >>> match(ob(legs=0, habitat='water'), fish)
    True
    >>> match(ob(Animal, legs=4), fish)
    False
    """

    def __init__(self, *args, **patterns):
        self.cls = None
        if args:
            if len(args) != 1:
                raise TypeError, "ob() takes at most 1 non-named arguments."
            self.cls = args[0]
        self.patterns = patterns
        

    def match(self, value, match_values_box, cap_val):
        if self.cls and not isinstance(value, self.cls):
            return False
        for attr, pattern in self.patterns.iteritems():
            if not hasattr(value, attr):
                return False
            if not match_recur(pattern, getattr(value, attr),
              match_values_box, cap_val):
                return False
        return True
    

ob = MatchOb



class MatchDict(MatchPattern):
    """
    Match for a dictionary, optionally matching against certain
    values of the dictionary. Alias is `dt()`.

    Examples:
    >>> match(dt(a=4, b='foo'), {'a': 4, 'b': 'foo', 'j': 9})
    True
    >>> match(dt(a=4, b='foo'), {'a': 4, 'j': 9})
    False
    >>> match(dt(), 3)
    False
    """

    def __init__(self, **patterns):
        self.patterns = patterns


    def match(self, value, match_values_box, cap_val):
        if not isinstance(value, dict):
            return False
        for attr, pattern in self.patterns.iteritems():
            if attr not in value:
                return False
            if not match_recur(pattern, value[attr], match_values_box, cap_val):
                return False
        return True


dt = MatchDict



class MatchType(MatchPattern):
    """
    Explicit type match. Alias is `type_is().`

    Matches only if the subject is an instance of the given type.

    >>> match(type_is(int), 3)
    True
    >>> match(type_is(int), int)
    False
    """

    def __init__(self, type):
        self.type = type


    def match(self, value, match_values_box, cap_val):
        return isinstance(value, self.type)


type_is = MatchType



class MatchPredicate(MatchPattern):
    """
    Match based on a predicate function. Alias is `pred()`.
    
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



class MatchCons(MatchPattern):
    """
    Match a python list as if it were a lisp cons cell. Alias is
    `cons()`.

    A cons cell is a basic implementation of a linked list,
    where each element is stored as a (car, cdr) pair.
    car is the value of the element, and cdr is the next
    cons cell in the list.

    Eg. [1, 2, 3, 4] is (1, (2, (3, (4, []))))
    
    So cons(2, [3, 4, 5]) matches [2, 3, 4, 5]

    Note that the current implementation is not efficient,
    the list is copied many times. This should not yet be
    used on large lists. @@
    
    Examples:
    
    >>> match(cons(1, cons(2, [])), [1, 2])
    True
    """
    
    
    def __init__(self, car_pattern, cdr_pattern):
        self.car_pattern = car_pattern
        self.cdr_pattern = cdr_pattern
    

    def match(self, value, match_values_box, cap_val):
        if not isinstance(value, list):
            return False
        
        if match_recur(self.car_pattern, value[0], match_values_box, cap_val):
            return match_recur(self.cdr_pattern, value[1:],
              match_values_box, cap_val)

        return False


cons = MatchCons



class MatchAll(MatchPattern):
    """
    Match a value only if all of the given paterns
    are satisfied by the value. Alias is `all()`.

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



class MatchSome(MatchPattern):
    """
    Match a value if at least one of the given patterns
    is matched by the value. Alias is `some()`.

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


## Value Capture

class ValueBox(MatchPattern):
    """
    A match expression that will match any expression and store
    its value in cap_val. This is the mechanism used for value
    capture.
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



class CapturedValues():
    """
    An object that creates ValueBoxes for capturing matched
    values.

    After a match is complete, the CapturedValues instance
    is switched into read mode, where it returns the matched
    values.

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


# Efficient cons slicing
# NOT DONE SOME OF THE MATH IS WRONG

class ListSlice:
    def __init__(lst, start, end=None):
        self.lst = lst
        self.start = start
        self.end = end

    def __get__(self, index):
        if self.end and index + self.start > self.end:
            raise IndexError, 'list index out of range'
        return self.lst[self.start + index]

    def __len__(self):
        if self.end is not None:
            return self.end - self.start
        return len(self.lst) - self.start

    def slice(start, end):
        return ListSlice(self.lst, self.start + start, self.start + self.end)

    def cons_split(self):
        return self.slice(0,1), self.slice(1)

