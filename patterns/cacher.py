# Кэширование результата функции через замыкание



def cached(func):
    storage = {}

    def func_(*args):
        print(args)
        if args not in storage:
            storage[args] = func(*args)

        return storage[args]

    return func_


@cached
def calc():
    return 5

calc()
