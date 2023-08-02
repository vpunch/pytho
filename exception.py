# Все исключения заканчиваются на Error


# Определяем собственный тип исключения
# Лучше не наследоваться от самого базового BaseException, все исключения, не
# связанные с системой, должны наследоваться от Exception
# Инициализатор первым аргументом принимает сообщение с описанием ошибки
# BaseException -> Exception -> User
class MyException(Exception):
    # Можно оставить пустым, инициализатор будет вызван из родителя
    pass


# Минимальная обработка
try:  # попробовать выполнить
    with open('foobarbah') as file:
        pass
except Exception:  # исключить
    print('Какая-то ошибка при открытии файла')

# Если класс исключения родительский, то будут также отлавливаться все дочерние
# классы

# Класс исключения можно вообще не указывать, тогда будут обработаны все
# исключения, но так делать не нужно, потому что можно замаскировать баги

def f():
    try:
        #print(foo)
        #1 / 0
        #4..split()
        #1 / [1]
        # Можем генерировать свои ошибки. Для этого нужно создать объект и
        # выбросить его при помощи raise
        # Можно не создавать объект явно, а просто указать класс
        #raise MyException

        print('Выполнение блока или выражения прекращается, если возникла '
              + 'ошибка')
        #return True
    # Обработать несколько исключений
    # Присвоить объект исключения переменной error
    except (NameError, ZeroDivisionError) as error:
        print(type(error))  # <class '...Error'>
        print('Ошибка имени или деление на ноль')
        # Общий код для нескольких ошибок

        try:
            #raise error
            # Можно не указывать объект исключения явно
            raise
        except NameError:
            # Специфичный дополнительный код
            print('Ошибка имени')

        return False
    except AttributeError:  # обработать отдельно
        print('Ошибка атрибута')
    except ArithmeticError:
        # Базовые исключения следует указывать последними, чтобы они не
        # перекрывали дочерние
        # Поиск обработчика except выполняется сверху вниз, если один
        # найден, поиск остальных прекращается
        print('Какая-то арифметическая ошибка')
    else:
        print('Ошибок не было')
    finally:
        # Этот блок всегда выполяется перед return
        print('Этот текст выводится в любом случае, были ошибки или нет')

    return 10


# Исключение будет подниматься по стеку вызовов в поиске обработчика. Если
# обработчика не найдется, программа будет завершена.

# Программа продолжит выполнение с того места, где отработал обработчик, а не
# того, где произошла ошибка

try:
    print(f())
except TypeError:
    print('Пiймав из функции')


# try...except можно вкладывать друг в друга
