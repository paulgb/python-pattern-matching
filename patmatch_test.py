
import unittest

from patmatch import match, CapturedValues, ValueBox, all, some, pred, cons

class TestPatmatch(unittest.TestCase):
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
        cv = CapturedValues()
        assert match(cv.i, 3)
        self.assertEquals(3, cv.i)


    def testCaptureBadMatch(self):
        cv = CapturedValues()
        assert not match([(cv.a, cv.b), int], [(5, "bar"), "foo"])
        try:
            l = cv.a
            print cv._values
            assert False
        except KeyError:
            pass


    def testDeepCapture(self):
        cv = CapturedValues()
        assert match([[[cv.a, cv.b], (cv.c, cv.d)], 5], [[[1, 2], (3, 4)], 5])
        self.assertEquals(1, cv.a)
        self.assertEquals(2, cv.b)
        self.assertEquals(3, cv.c)
        self.assertEquals(4, cv.d)

    
    def testAll(self):
        cv = CapturedValues()
        assert match(all(cv.a, int), 4)
        self.assertEquals(4, cv.a)
        assert not match(all(cv.a, int), 9)

    
    def testSome(self):
        cv = CapturedValues()
        assert match(some(int, str), "abc")
        assert not match(some(int, str), [])
        assert match((cv.a, (cv.b, (cv.c, ()))), (1, (2, (3, ()))))
        self.assertEquals(1, cv.a)
        
        cv = CapturedValues()
        assert match(some((cv.a, (cv.b, (cv.c, ()))), [cv.a, cv.b, cv.c]), (1, (2, (3, ()))))
        self.assertEquals(1, cv.a)


    def testPredicate(self):
        assert match(pred(lambda x: x > 4), 7)
        assert not match(pred(lambda x: x > 4), 2)

    
    def testCons(self):
        cv = CapturedValues()
        assert match(cons(cv.a, cv.b), [1,2,3])
        self.assertEquals(1, cv.a)
        self.assertEquals([2, 3], cv.b)
        

class TestCapturedValues(unittest.TestCase):
    def testSimple(self):
        cv = CapturedValues()
        k = cv.k
        k.match(7, [])
        cv._close()
        self.assertEquals(7, cv.k)

if __name__ == '__main__':
    unittest.main()


