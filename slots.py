import sys
from timeit import timeit


def change(o):
    o.second += 1
    del o.second
    o.second = 2


class Hard:
    def __init__(self):
        self._first = 1
        self.second = 2


class Slim:
    # Можно указать пустой кортеж, чтобы запретить определять атрибуты
    # экземпляра
    __slots__ = ('_first', 'second')

    def __init__(self):
        Hard.__init__(self)

    @property
    def first(self):
        return self._first

    @first.deleter
    def first(self):
        del self._first


class SlimHard(Slim):
    pass


class SlimSlim(Slim):
    __slots__ = ('color',)


hard = Hard()
slim = Slim()

# Теперь экземпляр не имеет магического словаря
#print(slim.__dict__)  # object has no attribute '__dict__'
print(Slim.__dict__)

# Слоты позволяют уменьшить размер **экземпляра** и ускорить доступ к атрибутам
print(sys.getsizeof(slim))                                 # 48
print(sys.getsizeof(hard) + sys.getsizeof(hard.__dict__))  # 152
print(timeit(lambda: change(hard)))  # 0.21
print(timeit(lambda: change(slim)))  # 0.17

# Слоты ограничивают **создание атрибутов экземпляра**, но их можно создать в
# классе
#slim.third = 3  # error: object has no attribute
Slim.third = 3
# Можем читать любые существующие атрибуты
print(slim.third)  # 3

# Слоты не гарантируют наличие указанных атрибутов, они только ограничивают
# создание
# Также слоты не ограничивают свойства
del slim.first

# Если не определить слоты в наследнике, то у экземпляра будет магический
# словарь
slim_hard = SlimHard()
slim_hard.fourth = 4
slim_hard.second = 'second'
# Но значений слотов там не будет, они хранятся отдельно
print(slim_hard.__dict__, slim_hard.second)  # {'fourth': 4}, 'second'

# Если определить слоты в наследнике, то слоты просто будут расширены
slim_slim = SlimSlim()
#slim_slim.fourth = 4  # error: object has no attribute
