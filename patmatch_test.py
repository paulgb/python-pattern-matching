
import unittest

from patmatch import match, MatchValues, ValueBox, all, some

class TestPatmatch(unittest.TestCase):
    """
    def testValue(self):
        assert match(1, 1)
        assert not match(1, 'foo')
        assert not match(1, 2)


    def testSequence(self):
        assert match((1, int), (1, 2))
        assert not match((1, 2), [1, 2])


    def testDeepSequence(self):
        assert match([(int, (str, dict))], [(3, ("foo", {}))])


    def testTypesMatch(self):
        assert match([int, str, dict], [2, 'foo', {}])
        assert not match([int, str], [2, 'foo', {}])
        assert not match([int, int, int], [2, 'foo', {}])
        assert match(dict, {})


    def testCaptureValues(self):
        mv = MatchValues()
        assert match(mv.i, 3)
        self.assertEquals(3, mv.i)


    def testCaptureBadMatch(self):
        mv = MatchValues()
        assert not match([(mv.a, mv.b), int], [(5, "bar"), "foo"])
        try:
            l = mv.a
            print mv._values
            assert False
        except KeyError:
            pass


    def testDeepCapture(self):
        mv = MatchValues()
        assert match([[[mv.a, mv.b], (mv.c, mv.d)], 5], [[[1, 2], (3, 4)], 5])
        self.assertEquals(1, mv.a)
        self.assertEquals(2, mv.b)
        self.assertEquals(3, mv.c)
        self.assertEquals(4, mv.d)

    
    def testAll(self):
        mv = MatchValues()
        assert match(all(mv.a, int), 4)
        self.assertEquals(4, mv.a)
        assert not match(all(mv.a, int), 9)
    """

    
    def testSome(self):
        """
        mv = MatchValues()
        assert match(some(int, str), "abc")
        assert not match(some(int, str), [])
        assert match((mv.a, (mv.b, (mv.c, ()))), (1, (2, (3, ()))))
        self.assertEquals(1, mv.a)
        """
        
        mv = MatchValues()
        assert match(some((mv.a, (mv.b, (mv.c, ()))), [mv.a, mv.b, mv.c]), (1, (2, (3, ()))))
        self.assertEquals(1, mv.a)
        

"""
class TestMatchValues():
    def testSimple(self):
        mv = MatchValues()
        k = mv.k
        k.set(7)
        mv._close()
        self.assertEquals(7, mv.k)
"""

if __name__ == '__main__':
    unittest.main()


