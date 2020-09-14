from abc import ABC, abstractmethod


class LogRecord:
    """
        Логируемые параметры
    """
    def __init__(self, name, start_time, status, execution_time):
        """
            Инициализация класса
            :param name - имя ресурса
            :param start_time - время запуска проверки ресурса
            :param status - статус ответа
            :param execution_time - время выполнения запроса к ресурсу
        """
        self.name = name
        self.start_time = start_time
        self.status = status
        self.execution_time = execution_time

    def __str__(self):
        return (f'{self.start_time}: {self.name}\t{self.status}\t'
                f'{self.execution_time}')


class LoggerRepository(ABC):
    """ Базовый класс для всех логеров """

    def __init__(self, queue, *args, **kwargs):
        self._queue = queue


    @abstractmethod
    def add_record(self, record: LogRecord):
        """
            Добавление записи в лог
            :param record - логируемая запись
        """
        pass


class LoggerFile(LoggerRepository):

    def __init__(self, queue, *args, **kwargs):
        super().__init__(queue, args, kwargs)
        try:
            filename = kwargs.get('filename')
        except KeyError:
            raise ValueError('Key filename missing in logger')

        self.fl = open(filename, "ta")

    def __del__(self):
        self.fl.close()

    def add_record(self, record: LogRecord):
        self.fl.write(f'{record}\n')
        self._queue.enqueue(record)


class LoggerFactory():
    """ Создает логер в зависимости от типа """

    @staticmethod
    def create_logger(type, queue, *args, **kwargs) -> LoggerRepository:

        logger_type = {
            "file": LoggerFile,
        }

        try:
            logger = logger_type.get(type)
            return logger(queue=queue, *args, **kwargs)
        except KeyError:
            raise ValueError("Unknown logger type")