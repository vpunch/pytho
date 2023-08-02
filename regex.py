re.match(что, где) -> result | None
result.group() == result.group(0)
result.start()
result.end()

re.search то же самое, но ищет не только в начале строки, вернет первое
нахождение

re.findall(что, где) -> list  то же самое, но возвращает все вхождения

re.split
re.sub
re.compile
