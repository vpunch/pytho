  # Журналирование это отслеживание событий, которые происходят во время
  # работы приложения
  # print используется для вывода во время обычного использования
  # программы
  # Уровни (важность событий) в порядке возрастания:
  # - DEBUG -- .debug(),
  # - INFO --  .info(),
  # - WARNING -- .warning(),
  # - ERROR -- .error(),
  # - CRITICAL -- .critical()
  # Корневой логер имеет уровень WARNING

  # .exception('message') можно использовать в блоке except, чтобы
  # вывести сообщение с уровнем ERROR, а также информацию об исключении

  # Самый простой способ настроить логер:
  #logging.basicConfig(
  #    filename='foobar.log',  # консоль по умолчанию
  #    level=logging.DEBUG,
  #    filemode='w',  # 'a' по умолчанию
  #    # %(asctime)s -- время
  #    # %(levelname)s -- уровень,
  #    # %(name)s -- имя логера
  #    format='%(message)s',
  #)
  # Передать событие корневому логеру:
  # logging.info('Самый простой способ')
  # logging.debug('%s с параметрами %s', 'first', 'second')

  # Определяет формат вывода записи
  FORMATTER: Final = logging.Formatter(
          Back.MAGENTA + '%(name)s | %(message)s' + Back.RESET)

  # Обработчик получает запись и отправляет ее куда-нибудь
  # В данном случае выводит на консоль
  HANDLER: Final = logging.StreamHandler(sys.stdout)
  HANDLER.setFormatter(FORMATTER)
  HANDLER.setLevel(logging.DEBUG)

  # Если уровень логера не выше уровня события, то он
  # - создает запись (LogRecord),
  # - передает ее обработчикам,
  # - передает запись родительскому логеру, если logger.propagate = True (
  #   по умолчанию)
  # Получать логер нужно этой функцией, первым аргументом передается имя
  # логера
  # Иерархия логеров определяется именем: слева от имени логера должна
  # быть цеопчка имен родительских логеров, имена разделяются точкой
  LOGGER: Final = logging.getLogger('main')
  LOGGER.addHandler(HANDLER)
  LOGGER.setLevel(logging.DEBUG)
