# coding=utf8
"""
Клиенты для API предоставляемого сайтом http://api.duma.gov.ru

http://api.duma.gov.ru/pages/dokumentatsiya/spravochnik-po-api

Примеры Использования:

>>> token = ''
>>> app_token = ''
>>> app_cli = JSONClient(token, app_token)
>>> stages = app_cli.stages()
>>> for stage in stages:
...    print stage['id'], stage['name']
...    for phase in stage['phases']:
...        print '\t',  phase['id'], phase['name']
"""
import json
import urllib2
from urllib import urlencode
from urlparse import urljoin

__all__ = ['BaseClient', 'JSONClient']


class BaseClient(object):
    """Базовый клиент API"""

    BASE_URL = "http://api.duma.gov.ru/api/"

    VALID_FORMATS = ['json', 'xml', 'rss']

    def __init__(self, token, app_token=None, response_format=None):
        self.token = token
        self.base_url = urljoin(self.BASE_URL, self.token) + '/'
        self.app_token = app_token
        if response_format:
            self.response_format = self._validate_format(response_format)
        else:
            self.response_format = None

    def _validate_format(self, _format):
        if _format in self.VALID_FORMATS:
            return _format
        else:
            raise ValueError('invalid format: %r' % _format)

    def _request(self, api_endpoint, response_format=None, **kwargs):
        """Builds API URI, perform HTTP request and returns response"""
        if response_format:
            _format = self._validate_format(response_format)
        elif self.response_format:
            _format = self.response_format
        else:
            raise ValueError('response_format must be provided')

        # FIXME RSS is valid only for search and does not require token in URL
        uri = urljoin(self.base_url, api_endpoint + '.' + _format)
        params = kwargs.copy()
        if self.app_token:
            params['app_token'] = self.app_token
        query = urlencode(params)
        url = uri + '?' + query
        data = urllib2.urlopen(url)
        return data.read()

    def topics(self):
        """Список тематических блоков.

        Источник: http://api.duma.gov.ru/pages/dokumentatsiya/spisok-tematicheskih-blokov
        """
        return self._request('topics')

    def classes(self):
        """Список отраслей законодательства.

        Источник: http://api.duma.gov.ru/pages/dokumentatsiya/spisok-otrasley-zakonodatelstva
        """
        return self._request('classes')

    def deputies(self, begin=None, position=None, current=None):
        """Список депутатов Государственной Думы и членов Совета Федерации.

        Параметры:
            begin — начало ФИО депутата ГД или члена СФ, может быть многобуквенным

            position — тип персоналии, может принимать значения "Депутат ГД" и "Член СФ"

            current — позволяет выбрать депутатов ГД и членов СФ, которые входят
                только в текущий созыв. Разрешенные значения: 1, "true", 0, "false".

        Источник: http://api.duma.gov.ru/pages/dokumentatsiya/spisok-deputatov-gd-i-chlenov-sf
        """
        params = {}
        if begin:
            params['begin'] = begin
        if position:
            params['position'] = position
        if current is not None:
            params['current'] = int(current)
        return self._request('deputies', **params)

    def committees(self, current=None):
        """Список комитетов

        Параметры:

            current — позволяет получить список комитетов, действующих (значения 1, true)
            или не действующих (значения 0, false) в данный момент.

        Источник: http://api.duma.gov.ru/pages/dokumentatsiya/spisok-komitetov
        """
        params = {}
        if current is not None:
            params['current'] = int(current)
        return self._request('committees', **params)

    def regional_organs(self, current=None):
        """Список региональных органов власти

        Параметры:

            current — позволяет получить список региональных органов власти, действующих (значения 1, true)
            или не действующих (значения 0, false) в данный момент.

        Источник: http://api.duma.gov.ru/pages/dokumentatsiya/spisok-regionalnih-organov-vlasti
        """
        params = {}
        if current is not None:
            params['current'] = int(current)
        return self._request('regional-organs', **params)

    def federal_organs(self, current=None):
        """Список федеральных органов власти

        Параметры:

            current — позволяет получить список федеральных органов власти, действующих (значения 1, true)
            или не действующих (значения 0, false) в данный момент.

        Источник: http://api.duma.gov.ru/pages/dokumentatsiya/spisok-federalnih-organov-vlasti
        """
        params = {}
        if current is not None:
            params['current'] = int(current)
        return self._request('federal-organs', **params)

    def stages(self):
        """Список стадий рассмотрения

        Источник: http://api.duma.gov.ru/pages/dokumentatsiya/spisok-stadiy-rassmotreniya
        """
        return self._request('stages')

    def instances(self, current=None):
        """Список инстанций рассмотрения

        Параметры:

            current — позволяет получить список инстанций, действующих (значения 1, true) или
            не действующих (значения 0, false) в данный момент.

        Источник: http://api.duma.gov.ru/pages/dokumentatsiya/spisok-instantsiy-rassmotreniya
        """
        params = {}
        if current is not None:
            params['current'] = int(current)
        return self._request('instances', **params)

    def periods(self):
        """Список созывов и сессий

        Источник: http://api.duma.gov.ru/pages/dokumentatsiya/spisok-sozivov-i-sessiy
        """
        return self._request('periods')

    def search(self, **params):
        """Поиск по законопроектам

        Ответ на запрос содержит записи с законопроектами,
        а также последние события по каждому из законопроектов.

        Все параметры являются необязательными.

        Параметры с заданными значениями

        law_type — тип законопроекта, возможны следующие значения:
        38 — Федеральный закон
        39 — Федеральный конституционный закон
        41 — Закон о поправках к Конституции РФ
        status — статус законопроекта, возможны следующих значения:
        1 — внесенные в ГД
        2 — находящиеся на рассмотрении ГД
        3 — входящие в примерную программу
        4 — входящие в программы комитетов
        5 — внесенные в ГД помимо программ
        6 — рассмотрение которых завершено
        7 — подписанные Президентом РФ
        8 — отклоненные (снятые) ГД
        9 — отозванные или возвращенные СПЗИ
        99 — рассмотрение которых завершено по прочим причинам
        Параметры с произвольными значениями

        name — название законопроекта
        number — номер законопроекта
        registration_start — минимальная дата регистрации законопроекта в формате ГГГГ-ММ-ДД
        registration_end — максимальная дата регистрации законопроекта в формате ГГГГ-ММ-ДД
        document_number — номер документа, связанного с законопроектом. Номер можно увидеть, например, в правой колонке на странице законопроекта в АСОЗД
        Параметры со значениями из справочников

        topic — идентификатор тематического блока
        class — идентификатор отрасли законодательства
        federal_subject — идентификатор федерального органа власти — субъекта законодательной инициативы
        regional_subject — идентификатор регионального органа власти — субъекта законодательной инициативы
        deputy — идентификатор депутата ГД или члена СФ — субъекта законодательной инициативы
        responsible_committee — идентификатор ответственного комитета
        soexecutor_committee — идентификатор комитета-соисполнителя
        profile_committee — идентификатор профильного комитета
        Параметры поиска по событиям

        По каждому из законопроектов в системе АИС «Законопроект» хранятся все события, произошедшие с ним. В запросе доступна фильтрация законопроектов по параметрам, связанными с событиями. Для активации поиска по данным параметрам обязательно указание режима поиска по событиям, за что отвечает параметр search_mode.

        search_mode — режим поиска по событиям законопроекта, возможны следующие значения:
        1 — поиск по всем событиям
        2 — поиск по последнему событию
        3 — поиск по ожидаемому событию
        После указания search_mode активируются следующие параметры поиска:

        event_start — минимальная дата события в формате ГГГГ-ММ-ДД
        event_end — максимальная дата события в формате ГГГГ-ММ-ДД
        instance — идентификатор инстанции рассмотрения
        stage — идентификатор стадии рассмотрения
        phase — идентификатор события рассмотрения
        Параметры stage и phase взаимоисключающие. Параметр phase позволяет фильтровать по типу события, т.е. производить более точную фильтрацию по сравнению с параметром stage.

        Прочие параметры

        page — номер запрашиваемой страницы результатов, по умолчанию равно 1
        limit — количество результатов на странице, допустимые значения: 5, 10, 20 (по умолчанию)
        sort — способ сортировки результатов, по умолчанию равно last_event_date, допустимые значения:
        name — по названию законопроекта
        number — по номеру законопроекта
        date — по дате внесения в ГД (по убыванию)
        date_asc — по дате внесения в ГД (по возрастанию)
        last_event_date — по дате последнего события (по убыванию)
        last_event_date_asc — по дате последнего события (по возрастанию)
        responsible_committee — по ответственному комитету

        Источник: http://api.duma.gov.ru/pages/dokumentatsiya/poisk-po-zakonoproektam
        """
        return self._request('search', **params)


class JSONClient(BaseClient):
    """Клиент API запрашивающий данные в JSON формате и осуществляющий их десериализацию"""

    def __init__(self, token, app_token=None):
        super(JSONClient, self).__init__(token, app_token, 'json')

    def _request(self, api_endpoint, response_format=None, **kwargs):
        json_data = super(JSONClient, self)._request(api_endpoint, response_format, **kwargs)
        return json.loads(json_data)
