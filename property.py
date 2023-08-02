# Дескрипторы нужны для управления чтением и записью атрибутов

# Альтернативный подход к созданию свойств, который позволяет сразу для
# нескольких свойств реализовать общую логику
class Descriptor:
    # Вызывается в момент создания экземпляра (d1 = Descriptor())
    def __set_name__(self,   # экземпляр дескриптора
                     owner,  # класс, в котором создается дескриптор
                     name):  # имя экземпляра дескриптора
        # Запоминаем имя атрибута, с которым будем работать
        self.data_key = '_' + name

    # Взывается в момент чтения экземпляра (instance.d1)
    def __get__(self,
                instance,  # экземпляр класса-владельца
                owner=None):
        # Возвращаем значение нашего атрибута
        #return instance.__dict__[self.data_key]

        # В идеале мы не должны обращаться к магическим атрибутам напрямую,
        # поэтому лучше переписать так
        return getattr(instance, self.data_key)

    # Вызывается в момент записи в экземпляр (instance.d1 = value)
    # В отличие от свойств, определяемых через декоратор, отсутствие сеттера не
    # приведет к исключению при попытке записи, просто будет использован
    # соответствующий локальный атрибут
    def __set__(self, instance, value):
        # Записываем значение, которое было присвоено дескриптору, в
        # управляемый атрибут
        instance.__dict__[self.data_key] = value

    def __delete__(self, instance):
        delattr(instance, self.data_key)

# Код для работы со свойствами классов,
# геттеры, сеттер, магия свойств

class A:
    d1 = Descriptor()
    d2 = Descriptor()

    # Определяем свойство (интерфейс для работы с атрибутом)
    # Более красивая альтернатива явным геттерам и сеттерам
    # meters = property(getter, setter)
    # или
    # meters = property()
    # meters = meters.setter(setter)
    # meters = meters.getter(getter)
    # или

    @property
    def meters(self):
        return self._meters

    # Если определить только геттер, без сеттера, то будет ошибка при записи
    # Свойства будут вызываться в том числе внутри класса, например, в
    # инициализаторе
    @meters.setter
    def meters(self, cm):
        self._meters = cm / 100

    @meters.deleter
    def meters(self):
        del self._meters
        # имеется также deleter, который вызывается при удалении


    # Вызывается при любом чтении атрибута, включая функцию getattr
    # Мы не можем обращаться к атрибутам self, иначе эта функция попадет в
    # рекурсию
    def __getattribute__(self, name):
        # Должна вернуть значение атрибута

        # Скрываем атрибут secret
        if name == 'secret':
            return '******'

        # Если атрибут не найден, то по умолчанию выбрасывает исключение
        #return super().__getattribute__(name)
        # Или можем вызывать метод из базового класса и передать ему текущий
        # контекст
        return object.__getattribute__(self, name)


    # Вызывается, когда __getattribute__ выбрасывает исключение (атрибут не был
    # найден)
    def __getattr__(self, name):
        # Можем для всех отсутствующих атрибутов возвращать None, чтобы было
        # похоже на js

        # Возвращаем значение атрибута, которого на самом деле нет, поэтому
        # должны переопределить __dir__ и добавить его туда
        if name == 'nexists':
            return None

        # У базового класса не определен __getattr__ по умолчанию, мы не можем
        # его вызвать


    # Вызывается, когда мы хотим присвоить значение атрибуту, в том числе при
    # помощи функции setattr
    def __setattr__(self, name, value):
        # Мы не можем записать значение непосредственно в self, так как
        # метод войдет в рекурсию
        super().__setattr__(name, value)

        # Или можем сделать это вручную при помощи словаря
        # Будет вызван .__getattribute__('__dict__'), но не .__setattr__
        # Но это будет записывать значения в обход сеттеров
        #self.__dict__[name] = value

    # Вызывается, когда надо удалить атрибут, например, при помощи del,
    # delattr
    def __delattr__(self, name):
        # Здесь мы должны именно удалить атрибут, если это не сделать, то он
        # останется у объекта
        super().__delattr__(name)


    # self[item] -> self.__getitem__(item)
    def __getitem__(self, item):
        return self.valid_colors[item]

    # self[key] = value -> self.__setitem(key, value)
    #def __setitem__(self, key, value):
    #    if len(self.color) > key:
    #        self._valid_colors.extend([None] * diff)

    #    pass

    # del self[key] -> self.__delitem__(key)
    #def __delitem__(self, key)


print(b11.secret)   # '******'
print(b11.nexists)  # None

b11.meters = 177
print(b11.meters)  # 1.77

print('Дескрипторы')
b11.d1 = 'foo'
b11.d2 = 'bar'
# Чтение из дескриптора
print(b11.d2) # 'bar'
# Прямой доступ к управляемому дискриптором атрибуту
print(b11.__dict__['_d2'])  # 'bar'
del b11.d2
print('_d2' not in b11.__dict__)  # True
