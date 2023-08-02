# Работа с примитивными типами

# Основные типы

print(type('Ivan'))        # <class 'str'>
print(type('foo') is str)  # True
print(type(str))           # <class 'type'>

print(type(10) is int)         # <class 'int'>
print(type(.1))                # <class 'float'>
print(type(True))              # <class 'bool'>


# Коллекции

print(type([1, '2', False]))   # <class 'list'>
print(type({'foo': 3, 1: 2}))  # <class 'dict'>
print(type({'foo', 1}))        # <class 'set'>


# Объекты

print(type(object()))  # <class 'object'>
print(type(lambda d: pass))
