# Цепочка отношений экземпляров к классам
# Объект    Объект  Тоже объект
# Примитив  Тип     Метакласс
# False ->  bool    -> type

print(isinstance(False, bool))  # True
print(isinstance(bool, type))  # True

# Семантика type отличается в зависимости от контекста. Если вызываем с одним
# аргументом, то возвращает нам тип значения, иначе это метакласс.

print(type(5))  # <class 'int'>


class Foo:
    pass


# Динамически создаем новый тип данных
Bar = type(
    'Bar',   # cls.__name__ -- имя
    (Foo,),  # cls.__bases__ -- наследники
    {'field': False, 'method': lambda self: self.field}  # cls.__dict__
)

print(Bar().method())  # False


# Функция-метакласс, которая используется для создания других классов
def get_metaclass(name, bases, attrs):
    attrs.update({'__foo': 'bar', 'a': 1})
    return type(name, bases, attrs)


class Meta(type):
    def __new__(cls, name, base, attrs):
        # Здесь класс-экземпляр еще не создан, поэтому можем изменить attrs
        attrs['a'] = 1

        return super().__new__(cls, name, base, attrs)

    def __init__(cls,   # ссылка на созданный класс
                 name,  # имя созданного класса
                 bases,
                 attrs):
        print(f'Инициализация нового класса: {cls}')

        # Класс уже создан, изменения в attrs на него не повлияют
        #attrs.update(

        # super(Meta, cls)
        super().__init__(name, bases, attrs)

        # Поэтому мы можем определить атрибуты через объект класса
        setattr(cls, '__foo', 'bar')

    #def __call__(cls):


#class MyClass(metaclass=get_metaclass):
class MyClass(metaclass=Meta):
    def get_foo(self):
        return getattr(self, '__foo')


o = MyClass()
print('__foo' in MyClass.__dict__)  # True
print(o.get_foo(), o.a)          # bar





# В определении класса мы используем синтаксис очень похожий на вызов функции
# не просто так

#class C(mataclass=Meta):
#    pass
#
#c = C()
#print(c)




# Все стандартные типы данных порождены метаклассом type
#print(isinstance(False, bool))  # True
#print(isinstance(bool, type))   # True

# Типом стандартного типа данных является type
#print(type(bool) is type)  # True
# И типом определенного класса тоже будет type
#print(type(B1) is type) # True


#print(isinstance(B, type))  # False


# Создали объект и сохранили ссылку на него в o
# Имеет тип object
#o = object()
#print(type(o))    # <class 'object'>
#
#print(type(B2))  # <class 'type'>
#print(type(fooo)) # <class '__main__.Foo'>
