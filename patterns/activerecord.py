# Метакласс, который изменяет классы таким образом, что экземпляры получают
# значения атрибутов из соответствующей таблицы в базе данных
# Active Record (AR) -- шаблон, где таблицы это классы, а записи экземпляры

_TABLE = [
    {'first': 1, 'second': 2, 'third': 3},
    {'first': 11, 'second': 22, 'third': 33},
]


class Connector(type):
    @staticmethod
    def connect(self, attrs):
        row = _TABLE[self.__index]

        for attr in attrs:
            if not attr.startswith('__'):
                setattr(self, attr, row[attr])

        self.__class__.__index += 1

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        cls.__index = 0
        # Получаем атрибут из метакласса через класс
        # У экземпляра cls доступа к этому атрибуту нет, у него своя цепочка
        # наследования
        cls.__init__ = lambda self: cls.connect(self, attrs)




class Row(metaclass=Connector):
    first = 'first'
    second = 'second'
    third = 'third'


row1 = Row()
row2 = Row()

#print(row1.connect)  # error: 'Row' object has no attribute 'connect'
print(Row.connect)   # <function Connector.connect...

print(row1.first)
print(row2.first)
