    # Цикл for и встроенная функция iter() взывает этот магический метод для
    # получения итератора объекта
    def __iter__(self):
        # Экземпляр сам является итератором
        self.step = 1
        return self

    # Вызывается встроенной функцией next() при итерации
    # Итератор это объект, у которого определен магический метод __next__
    def __next__(self):
        step = 1
        value = getattr(self, 'current', 0)

        if value > self.distance:
            raise StopIteration

        self.current = value + step
        return value
