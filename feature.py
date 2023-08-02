# Копирование элементов в массив

inil = [1, 2, 3]
l = inil
l[1:2] = [4, 5]
print(inil is l, l)  # True, [1, 4, 5, 3]
l[:] = [1]
print(l)  # [1]

# Слияние словарей
fd = {'x': 1}
sd = {'a': 1}
print(fd | sd)       # {'x': 1, 'a': 1}
print({**fd, **sd})  # {'x': 1, 'a': 1}


# Меняем местами значения
left = 1
right = 10
print(left, right)
left, right = right, left
print(left, right)
