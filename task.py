from abc import ABC, abstractmethod
import asyncio
import requests
from enums import CheckStatusEnum
import time
from logger import LoggerRepository, LogRecord
from datetime import datetime


class Task(ABC):
    """ Базовый абстрактный класс, представляющий задачу по мониторингу сайта"""

    def __init__(
            self, name, uri, search_content, check_period_ms, timeout_ms,
            *args, **kwargs):
        """
            Инициализация класса
            :param name - имя задачи
            :param uri - URI задачи
            :param search_content - паттерн для поиска в контенте ответа
            :param check_period_ms - период проверки в миллисекундах
            :param timeout_ms - таймаут сетевых операций в миллисекундах
        """
        self.name = name
        self.uri = uri
        self.search_content = search_content
        self.check_period_ms = check_period_ms
        self.timeout_ms = timeout_ms

    @classmethod
    @abstractmethod
    def is_task_for(cls, uri) -> bool:
        """
            Проверяет, подходит ли данная задача для проверки URI

            param: uri - URI задачи
            :return булеово значение
        """
        pass

    async def start_check(self, logger: LoggerRepository):
        """ Запуск цикла проверок """
        while True:
            start_time = datetime.now()
            status, execution_time = await self.check()
            record = LogRecord(
                name=self.name,
                start_time=start_time,
                status=status,
                execution_time=execution_time,
            )
            print(record)
            lock = asyncio.Lock()
            async with lock:
                logger.add_record(record)

            await self.sleep()

    @abstractmethod
    async def check(self) -> CheckStatusEnum:
        """
            Проверка задания задачи

            :return статус проверки
        """
        pass

    async def sleep(self):
        """ Пауза между повторами задачи"""
        await asyncio.sleep(self.check_period_ms/1000)

    @abstractmethod
    def _request(self, *args, **kwargs):
        """
            Запрос к проверяемому ресурсу

            :return список {
                код ответа,
                контент
                время выполнения запроса
            }
        """
        pass

    @abstractmethod
    def _check_content(self, content):
        pass


class HttpTask(Task):

    @classmethod
    def is_task_for(cls, uri):
        return uri.lower().startswith('http://')

    async def check(self):
        status, content, execution_time = self._request()

        if status == CheckStatusEnum.ok:
            status = self._check_content(content)

        return status, execution_time

    def _request(self):
        start_time = time.process_time()
        status_code = CheckStatusEnum.request_failed
        content = None
        try:
            r = requests.get(self.uri, timeout=self.timeout_ms/1000)
            if r.status_code == 200:
                status_code = CheckStatusEnum.ok
                content = r.text
        except requests.exceptions.Timeout:
            status_code = CheckStatusEnum.request_timeout
        except:
            # TODO request возращает много разных исключений, необходимо
            #  научиться их обрабатывать
            pass

        execution_time = time.process_time() - start_time

        return status_code, content, execution_time

    def _check_content(self, content):
        status = CheckStatusEnum.ok
        if self.search_content:
            if content:
                if self.search_content not in content:
                    status = CheckStatusEnum.content_mismatch

        return status


class HttpsTask(HttpTask):

    @classmethod
    def is_task_for(cls, uri):
        return uri.lower().startswith('https://')

    async def check(self):
        status, content, execution_time = self._request()

        if status == CheckStatusEnum.ok:
            status = self._check_content(content)

        return status, execution_time

    def _request(self):
        return super()._request()


class TaskFactory():
    """ Создает таску в зависимости от URI """

    def __init__(self):
        self.registry = []

    def register_task_creator(self, task):
        self.registry.append(task)

    def create_task(self, name, uri,  *args, **kwargs) -> Task:
        for task in self.registry:
            if task.is_task_for(uri):
                return task(name, uri,  *args, **kwargs)

        raise ValueError("Unknown task type")






