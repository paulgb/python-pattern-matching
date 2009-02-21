
import unittest

from patmatch import match, CapturedValues, ValueBox, all, some, pred, cons, eq, type_is, ob, dt

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
        assert match(all(), 4)
    
    def testSome(self):
        cv = CapturedValues()
        assert match(some(int, str), "abc")
        assert not match(some(int, str), [])
        assert match((cv.a, (cv.b, (cv.c, ()))), (1, (2, (3, ()))))
        self.assertEquals(1, cv.a)
        
        cv = CapturedValues()
        assert match(some((cv.a, (cv.b, (cv.c, ()))), [cv.a, cv.b, cv.c]), (1, (2, (3, ()))))
        self.assertEquals(1, cv.a)

        cv = CapturedValues()
        assert match(some((cv.a, (cv.b, (cv.c, ()))), [cv.d, cv.e, cv.f]), [1, 2, 3])
        self.assertEquals(1, cv.d)
        
        try:
            cv.a
            assert False
        except KeyError:
            pass

    def testPredicate(self):
        assert match(pred(lambda x: x > 4), 7)
        assert not match(pred(lambda x: x > 4), 2)

    
    def testCons(self):
        cv = CapturedValues()
        assert match(cons(cv.a, cv.b), [1,2,3])
        self.assertEquals(1, cv.a)
        self.assertEquals([2, 3], cv.b)

    
    def testEq(self):
        assert match(eq('abc'), 'abc')
        assert match(eq(int), int)
        assert not match(eq(int), 4)
    

    def testType(self):
        assert match(type_is(int), 4)
        assert not match(type_is(int), int)


    def testObject(self):
        class Book:
            def __init__(self, title, author, year=None, publisher=None, location=None):
                self.title = title
                self.author = author
                self.year = year
                self.publisher = publisher
                self.location = location

        jazz = Book("Tales of the Jazz Age", "F. Scott Fitzgerald", 1922)
        selfish = Book("The Selfish Gene", "Richard Dawkins", 1976, "Oxford", "London")
        fifth = Book("Fifth Business", "Robertson Davies", 1970, "Penguin", "Toronto")

        cv = CapturedValues()
        assert match(ob(Book, title=cv.title, author=cv.author), jazz)
        self.assertEquals("Tales of the Jazz Age", cv.title)
        self.assertEquals("F. Scott Fitzgerald", cv.author)
        
        cv = CapturedValues()
        assert not match(ob(Book, abc=cv.abc), jazz)

        cv = CapturedValues()
        assert match(ob(Book, title=cv.title, author="Richard Dawkins", year=pred(lambda x: x > 1970)), selfish)
        self.assertEquals("The Selfish Gene", cv.title)

        cv = CapturedValues()
        assert match(ob(title=str, author=str, year=1970), fifth)

        cv = CapturedValues()
        assert not match(ob(Book, title=cv.title, author="Robertson Davies", year=pred(lambda x: x > 1970)), selfish)


    def testHash(self):
        cv = CapturedValues()
        assert match(dt(foo=cv.foo, baz=(1, cv.baz)), {'foo': 6, 'bar': 9, 'baz': (1, 3)})
        self.assertEquals(6, cv.foo)
        self.assertEquals(3, cv.baz)

    def testMultipleUses(self):
        cv = CapturedValues()
        assert match((cv.a, cv.b, cv.a), (1, 2, 1))
        self.assertEquals(1, cv.a)        
        self.assertEquals(2, cv.b)        

        cv = CapturedValues()
        assert not match((cv.a, cv.b, cv.a), (1, 2, 3))


if __name__ == '__main__':
    unittest.main()


