import configparser


class Configure:
    """ Класс, отвечающий за конфигурационные параметры системы """
    def __init__(self, configure_filename):
        """
            Инициализация класса
            :param configure_filename - путь к конфигурационному файлу
        """
        self._config = configparser.ConfigParser()
        self._config.read(configure_filename)

        self._sites = self._make_sites()
        self._check_period_ms, self._timeout_ms = self._default_params()

    def _make_sites(self):
        """
            Парсит конфигурацию на предмет сайтов

            :return словарь сайтов с параметрами
        """
        sites = {}
        for section in self._config.sections():
            if section.startswith('Site_'):
                sites[section] = {
                    'name': self._config[section].get(
                        'name',
                        fallback=f'No such name parametr in {section}'
                    ),
                    'uri': self._config[section].get(
                        'uri',
                        fallback=f'No such url parametr in {section}'
                    ),
                    'search_content': self._config[section].get(
                        'search_content', ''
                    ),
                }

        return sites

    def _default_params(self):
        """
            Возращает параметры по умолчанию

            :return список [
                период проверки в миллисекундах,
                таймаут сетевых операций в миллисекундах,
                ]
        """

        defaults = {
            'check_period_ms': 5000,
            'timeout_ms': 10000,
        }

        return [
            self._config.get('Default', 'check_period_ms', vars=defaults),
            self._config.get('Default', 'timeout_ms', vars=defaults),
        ]

    @property
    def sites(self):
        """
            Возращает список сайтов с параметрами, перечисленных в конфигурации

            :return словарь сайтов с параметрами
        """
        return self._sites

    @property
    def check_period_ms(self):
        """Период проверки в миллисекундах"""
        return int(self._check_period_ms)

    @property
    def timeout_ms(self):
        """Таймаут сетевых операций в миллисекундах"""
        return int(self._timeout_ms)







