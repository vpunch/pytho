# Магические атрибуты это такие же атрибуты, просто они скрыты и вызываются
# интепретатором неявно


# Магические атрибуты класса

class MyClass:
    # Приводит объект к строке для пользователя (str(object), print(object))
    def __str__(self):
        return self.color

    # Выводит отладочную информацию об объекте
    # Если __str__ не определен, то используется вместо него
    def __repr__(self):
        # object.__class__ содержит имя порождающего класса
        return f'{self.__class__}: {self.color}'

    # Позволяет применять функцию len() к экземплярам (вычисление длины)
    def __len__(self):
        return self.distance

    # Позволяет применять функцию abs() к экземплярам (вычисление модуля)
    def __abs__(self):
        return abs(self.distance)

    # Математические операции с экземпляром

    # self + other
    # __radd__(self, other) other + self
    # __iadd__(self, other) self += other
    # __sub__(self, other) self - other
    # __mul__(self, other)  self * other
    # __truediv__(self, other)  self / other
    # __floordiv__(self, other) self // other
    # __mod__(self, other)     self % other
    def __add__(self, other: int):
        try:
            self.validate_int(other)
        except:
            raise ArithmeticError('Неправильный операнд')

        result = type(self)()
        result.distance = self.distance + other

        return result

    # Операции сравнения с экземпляром

    # __eq__(self, other) self == other
    # По умолчанию объекты сравниваются по id
    # __ne__(self, other) self != other
    # Если __ne__ не определен, будет not (self == other)

    # __lt__(self, other) self < other
    # Если __lt__(self, other) не определен, то будет использован __gt__(other, self)
    # Аналогично для __gt__, __ge__ и __le__
    # Это сделано для того, чтобы не писать похожий зеркальный код
    # __gt__(self, ohter) self > other
    # __ge__(self, other) self >= other
    def __le__(self, other):
        return self.distance <= other.distance

    #

    # Возвращает результат встроенной функции hash для объекта
    # Хэш можно вычислить только для неизменяемого объекта, поэтому hash([1,
    # 2]) вернет ошибку
    # В качестве ключей словаря можно использовать только хешируемые (значит
    # неизменяемые) объекты
    # dictionary[self -> self.__hash__()] = value
    # По умолчанию хэш экземпляра считается от его адреса. Если мы
    # переопределим __eq__, то __hash__ будет неопределен, так как хэши равных
    # объектов должны быть равны
    #def __hash__(self):
    #    return hash(self.distance)


    # Настройка правдиаости экземпляров (правдивость это приведение к bool)
    # По умолчанию возвращает True для всех экземпляров
    # Но если __len__ определен, то возвращает bool(self.__len__())
    # Неявно вызывается в if
    #def __bool__(self):
    #    pass

    def __call__(self, *args, **kwargs):
        return 'Hello from instance call'


print('\nПрименение встроенных функций к экземпляру')
print(b11)
print(len(b11))
print(abs(b11))
print(b11 + 10)
print('\nВызов объекта')
print(b11())  # Hello from instance call



# Модуля

# Магический метод, позволяющий получить размер объекта. Лучше использовать
# sys.getsizeof
object.__sizeof__()

print(MyClass.__name__)  # имя класса
