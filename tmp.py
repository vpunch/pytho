def foo(**kwargs: any):
    print(kwargs)
    print(type(kwargs))


foo(a=1, b=2)
