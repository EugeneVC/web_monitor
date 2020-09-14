import threading
import os
from configure import Configure
from task import HttpTask, TaskFactory, HttpsTask
import asyncio
from logger import LoggerFactory
from flask import Flask, render_template
from flask_classful import FlaskView
import copy


class LastRecordQueue:
    """ Очередь, содержащая последние N записей лога"""

    def __init__(self, max_size):
        """
            Инициализация класса
            :param max_size - максимальный размер очереди
        """
        self._items = []
        self._max_size = max_size
        self._mutex = threading.Lock()

    def enqueue(self, item):
        """ Вставка элемента в очередь """
        with self._mutex:
            # при вставке, мы ограничиваем максимальный размер очереди
            if len(self._items) >= self._max_size:
                self._items.pop()
            self._items.insert(0, item)

    def dequeue(self):
        """ Получение элемента из очереди ( элемент удаляется) """
        with self._mutex:
            return self._items.pop()

    def size(self):
        """ Размер очереди """
        with self._mutex:
            return len(self._items)

    def items(self):
        """ Список элементов очереди """
        with self._mutex:
            return copy.deepcopy(self._items)


# очередь содержащая последние N записей лога
last_record_queue = LastRecordQueue(max_size=100)


class WebMonitorView(FlaskView):
    """ Класс, содержащий страницы сайта """
    def index(self):
        """ Главная страницы сайта """
        global last_record_queue
        return render_template('index.html', items=last_record_queue.items())


def run_flask_in_thread():
    """ Запукс flask сервера в потоке """
    flask_app = Flask(__name__)
    WebMonitorView.register(flask_app, route_base='/')
    flask_app.run(use_reloader=False)


class WebMonitor:
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

        self.logger = LoggerFactory.create_logger(queue=last_record_queue, **self.configure.logger)

    def run(self):

        loop = asyncio.get_event_loop()

        #регистрируем все задачи
        for task_param in self.configure.sites.values():
            task_param.update({
                'check_period_ms': self.configure.check_period_ms,
                'timeout_ms': self.configure.timeout_ms,
            })
            task = self.task_factory.create_task(**task_param)

            asyncio.ensure_future(task.start_check(self.logger))

        loop.run_forever()


if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask_in_thread)
    flask_thread.start()

    configure_filename = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'web_monitor.ini'
    )
    web_monitor = WebMonitor(configure_filename)
    web_monitor.run()



