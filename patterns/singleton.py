# Суть заключается в том, что нужно переопределить конструктор и сохранять
# объект в атрибут класса

class Foo:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, a, b):
        self.a = a
        self.b = b

foo1 = Foo(1, 2)
foo2 = Foo(3, 4)
print(foo1 is foo2)    # True
print(foo1.b, foo2.b)  # 4, 4
