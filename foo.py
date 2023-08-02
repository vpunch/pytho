#
#
#class A:
#    def do_thing(self):
#        print('From A')
#
#class B(A):
#    def do_thing(self):
#        print('From B')
#
#class C(A):
#    def do_thing(self):
#        print('From C')
#
#class D(B, C):
#    pass

#d = D()
#print(D.__mro__)  # d b c a
#d.do_thing()




class M(type):
    def foooo(self):
        print('from meta', self)

    def __new__(cls, name, base, attrs):
        print(attrs)
        return super().__new__(cls, name, base, attrs)

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

class A(metaclass=M):
    def fooo(self):
        print('from a')

class B(A):
    bar = 'bar'

    @classmethod
    def foo(cls):
        print(cls.bar)
    
    #pass
    #def foo(self):
        #super().foo()
        #print('from b')

b = B()
#b.foo()
#b.__init__()

B.fooo(b)
#b.fi()
B.foooo()
B.foo()

b.fooo()
#b.foooo()

#B.foo()

print(type(None))
print(type(A), type(M))
print([1, 2, 3][::-1])

