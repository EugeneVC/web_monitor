import sys
import os
from configure import Configure
from task import HttpTask, TaskFactory, HttpsTask
import asyncio


class WebMonitor():
    """ Основной класс утилиты мониторинга сайтов  """

    def __init__(self, configure_filename):
        """
            Инициализация класса
            :param configure_filename - путь к конфигурационному файлу
        """
        self.configure = Configure(configure_filename)

        self.task_factory = TaskFactory()
        self.task_factory.register_task_creator(HttpTask)
        self.task_factory.register_task_creator(HttpsTask)

    def run(self):

        loop = asyncio.get_event_loop()

        #регистрируем все задачи
        for task_param in self.configure.sites.values():
            task_param.update({
                'check_period_ms': self.configure.check_period_ms,
                'timeout_ms': self.configure.timeout_ms,
            })
            print(task_param)
            task = self.task_factory.create_task(**task_param)

            asyncio.ensure_future(task.start_check())

        loop.run_forever()


if __name__ == '__main__':
    configure_filename = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'web_monitor.ini'
    )
    web_monitor = WebMonitor(configure_filename)
    web_monitor.run()
