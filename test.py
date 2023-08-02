from string import ascii_letters

class Person:
    @staticmethod
    def parse_name(value):
        name_parts = value.split()

        checker = lambda symbol: symbol in ascii_letters + ' '

        if len(name_parts) != 3 or \
                not all(map(checker, value)):
            raise ValueError('Ошибка в ФИО')

        return name_parts

    @staticmethod
    def parse_age(value):
        if value < 14 or value > 120:
            raise ValueError('Ошибка в возрасте')

        return value

    @staticmethod
    def parse_code(value):
        code_parts = value.split()

        if len(code_parts) != 2 \
                or len(code_parts[0]) != 4 \
                or len(code_parts[1]) != 6:
            raise ValueError('Ошибка в паспорте')

        return code_parts

    @staticmethod
    def parse_w(value):
        if value < 20:
            raise ValueError('Ошибка в весе')

        return value

    def __init__(self, name, age, code, w):
        self.name = name
        self.age = age
        self.code = code
        self.w = w

    @property
    def name(self): return ' '.join(self._name)

    @name.setter
    def name(self, value): self._name = self.parse_name(value)

    @property
    def age(self): return self._age

    @age.setter
    def age(self, value): self._age = self.parse_age(value)

    @property
    def code(self): return ' '.join(self._code)

    @code.setter
    def code(self, value): self._code = self.parse_code(value)

    @property
    def w(self): return self._w

    @w.setter
    def w(self, value): self._w = self.parse_w(value)


person = Person('Foo Bar Bah', 33, '1234 123456', 70)

try: 
    second = Person('Foo Bar', 33, '1234 123456', 70)
except:
    print('Ошибка')

person = Person('Фу бар бах', 33, '1234 123456', 70)
