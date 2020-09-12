from abc import ABC, abstractmethod
import asyncio


class Task(ABC):
    """ Базовый абстрактный класс, представляющий задачу по мониторингу сайта"""

    def __init__(self, name, uri, *args, **kwargs):
        """
            Инициализация класса
            :param name - имя задачи
            :param uri - URI задачи
        """
        self.name = name
        self.uri = uri

    @classmethod
    @abstractmethod
    def is_task_for(cls, uri) -> bool:
        """
            Проверяет, подходит ли данная задача для проверки URI

            param: uri - URI задачи
            :return булеово значение
        """
        pass

    async def start_check(self):
        while True:
            await self.check()
            await self.sleep()

    #@abstractmethod
    async def check(self):
        """ Проверка задания задачи"""
        print(self.name)

    async def sleep(self):
        await asyncio.sleep(1)


class HttpTask(Task):

    @classmethod
    def is_task_for(cls, uri):
        return uri.lower().startswith('http://')


class HttpsTask(Task):

    @classmethod
    def is_task_for(cls, uri):
        return uri.lower().startswith('https://')


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

        return ValueError("Unknown task type")






