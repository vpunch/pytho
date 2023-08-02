# Описание данных и определение структуры данных

from dataclasses import dataclass, field, InitVar, make_dataclass
from pprint import pprint


# Можно указывать без аргументов
#@dataclass
# Либо с ними для настройки
@dataclass(init=False,    # создавать __init__ (он не используется и не нужен,
                          # если класс базовый, по умолчанию True)
           repr=True,     # создавать __repr__ (по умолчанию True)
           eq=True,       # создавать __eq__ (по умолчанию True)
           order=False,   # создавать __lt__ и __le__ (по умолчанию False)
           frozen=False,  # запретить присваивать значения любым атрибутам (по
                          # умолчанию False)
           slots=False)    # использовать слоты для экземпляров (по умолчанию
                          # False)
class Product:
    # Поля без аннотации типа не попадают в инициализатор
    # Порядок полей определяет порядок соответствующих параметров в
    # инициализаторе
    # Значение поля переносится в инициализатор экземпляра в качестве значения
    # по умолчанию, поэтому поля со значением должны быть в конце списка
    # В результирующем классе будут атрибуты только для полей со значением по
    # умолчанию

    name: str

    # field можно использовать для более тонкой настройкой полей
    # default -- значение по умолчанию,
    # repr -- отображать ли поле в выводе repr
    # compare -- использовать ли поле при сравнении экземпляров
    price: float = field(default=0., repr=False, compare=False)

    weight: int = 1

    # Нужно быть осторожней с объектами, которые присваиваются по ссылке
    # Мы не можем использовать изменяемые объекты, так как они будут общими для
    # всех экземпляров
    tags: tuple = ('tasty', 'profitable')

    # Инициализатор будет вызывать функцию default_factory, чтобы получить
    # значение атрибута
    # Теперь для каждого экземпляра будет создаваться свой новый список
    #dimensions: field(default_factory=list)
    dimensions: list = field(default_factory=lambda: [1, 2])

    # init=False исключает поле из инициализатора, но мы **должны** определить
    # этот атрибут после инициализации, например, в __post_init__()
    full_price: float | None = field(init=False)

    # InitVar используется для объявления псевдо-полей. Они не попадают в
    # экземпляр, а их значение (по умолчанию или из конструктора) передается в
    # __post_init__
    need_full_price: InitVar[bool] = False

    # Можем определить любые магические методы, декоратор не заменит их
    # Например, можно переопределить __eq__
    # Можно создать простые методы

    # Так как декоратор устанавливает свой инициализатор, можем определить
    # специальный магический метод, который будет вызыван в конце
    # инициализатора
    def __post_init__(self, need_full_price):
        if need_full_price:
            self.full_price = self.weight * self.price
        else:
            self.full_price = None


# При наследовании если один из классов заморожен, то все остальные должны быть
# замороженными
@dataclass(frozen=False)
class ExtdProd(Product):
    # Не попадет в инициализатор
    counter = 0

    id_: int = field(init=False)

    # В инициализаторе сначала идут поля из базового класса, затем из
    # наследника, поэтому если в родителе есть поля со значением по умолчанию,
    # то в наследнике все должны быть со значением по умолчанию

    # В наследнике можно переопределить поля из базового класса, порядок
    # при этом не изменится
    weight: float = 3

    def __post_init__(self, need_full_price):
        # Инициализатор вызывает self.__post_init__(), ближайший находится
        # здесь, поэтому базовый нужно вызывать вручную
        super().__post_init__(need_full_price)

        self.id_ = self.counter
        self.__class__.counter += 1


ep1 = ExtdProd('Огурец', 0., 0.1, need_full_price=True)
ep2 = ExtdProd(weight=0.1, name='Огурец')

print('Класс имеет все поля со значением по умолчанию')
pprint(Product.__dict__)
# True (есть значение по умолчанию), False (нету)
print([attr in Product.__dict__ for attr in ['price', 'dimensions']])

print('\nЭкземпляр тоже их имеет, но без неаннотированных и псевдо-полей')
pprint(ep1.__dict__)

print()
# Значения псевдополей не присваиваются классу
print(ep1.need_full_price, ep2.need_full_price)  # False, False
print(ep1.full_price, ep2.full_price)            # 0.0, None

# Отображает значения полей. Если поле определялось в __post_init__, без
# упоминания в теле класса (init=False), то в выводе его не будет, так как
# декоратор, который определяет __repr__, ничего о нем не знает
print('\nrepr')
print(ep1)  # ExtdProd(name='Огурец',
            #          weight=0.1,
            #          tags=('tasty', 'profitable'),
            #          dimensions=[1, 2],
            #          full_price=0.0,
            #          id_=0)
print(ep2.id_)  # 1

print('\neq')
print(ep1 == ep2, ep1 is ep2)  # True, False
#print(ep1 > ep2)

ep1.foo = 'bar'

ep1.dimensions.append(0.5)
# Новый элемент не появился во втором экземпляре
print(ep2.dimensions)  # [1, 2]


# Если нужно структуру динамически (в процессе работы программы)
Product_ = make_dataclass(
    'Product_', 
    [('foo', str), 'bar', ('bah', int, field(default=0))],
    namespace={'get_bar': lambda self: self.bar}
)

print(Product_('value', 1).get_bar())
