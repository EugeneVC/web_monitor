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

    @property
    def sites(self):
        """
            Возращает список сайтов с параметрами, перечисленных в конфигурации

            :return словарь сайтов с параметрами
        """
        return self._sites







