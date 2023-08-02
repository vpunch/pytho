# Менеджер контекста это класс, где реализованы магические методы, открытия и
# закрытия

v1 = [1, 2, 3]
v2 = [2, 3]

class MyManager:
    # Сра
    def __init__(self, v):
        self.__v = v

    def __enter__(self):
        self.__tv = self.__v.copy()
        return self.__tv

    # Вызывается в момент завершения работы или исключения
    def __exit__(self,
                 exc_type,  # тип исключения
                 exc_val,   # экземпляр исключения
                 exc_tb):   # трейсбек
        if exc_type is None:  # исключений не было
            self.__v[:] = self.__tv

        #return False  # выплюнуть исключение, которое сюда пришло
        return True  # подавить исключение, если было

try:
    # as <variable> можно не писать, если не хотим ссылаться на объект контекста
    with MyManager(v1) as v:
        for i in range(len(v)):
            v[i] += v2[i]
except:
    print('Поймали исключение')

print(v1)
# return внутри блока with работает аналогично finally: контекст закроется
# перед выходом

class Connection:
    def close(self):
        print('Closing...')

from contextlib import closing

# closing для вызова close у аргумента в конце контекста
# Контекст может работать с несколькими объектами
with closing(Connection()) as connection, closing(connection):
    pass

# 2 раза будет Closing...
