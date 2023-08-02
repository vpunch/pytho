class Derivat:
    def __init__(self, func):
        self.__func = func

    def __call__(self, x, dx=1e-6):
        dy = self.__func(x + dx) - self.__func(x)
        return dy / dx


def derivat(func):
    def wrapper(x, dx=1e-6):
        dy = func(x + dx) - func(x)
        return dy / dx

    return wrapper


#@Derivat
@derivat
def func(x):
    return x ** 2

func = Derivat(func)

# Производная функции в точке 2
print(func(2))
