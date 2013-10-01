# -*- coding: utf-8 -*-
"""
Инструменты конфигурирования хранилища
"""
import re
import importlib


IO_PURPOSE_INDEX = 'IO_PURPOSE_INDEX'
IO_PURPOSE_DATA = 'IO_PURPOSE_DATA'

IO_BACKEND = 'io_backend'
BASE_NAME = 'base_name'

QUERY_API = 'query_api'


def _import_thing(path, name, default_module):
    """
    Возвращает callable-объект по пути вида "package.modue.thing"
    :path - строка вида "package.module.callable",
            либо callable объект - такой возвращается сразу
    :name - наименование получаемого объекта (для сообщений об ошибках)
    :default_module - пусть к модулю, где объект ищется при отсутствии пути
    """
    if callable(path):
        return path

    try:
        module_name, attr = re.match(r'^(?:([\w.]*)\.)?(\w+)$', path).groups()
    except AttributeError:
        raise ValueError(
            'Bad %s name format: "%s"' % (name, path))

    module_name = module_name or default_module
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise ValueError(
            'Can\'t import the %s module: "%s"' % (name, module_name))

    try:
        thing = getattr(module, attr)
    except AttributeError:
        raise ValueError(
            'Module "%s" does not have an attribute "%s"' % (
                module_name, attr))

    if not callable(thing):
        raise TypeError(
            'The %s must be callable!' % name)

    return thing


def configure(**kwargs):
    cfg = {
        IO_BACKEND: 'memory',
        QUERY_API: 'Simple'
    }
    cfg.update(kwargs)

    cfg[IO_BACKEND] = _import_thing(
        cfg[IO_BACKEND], 'IO backend', 'pytoydb.io_backends')

    cfg[QUERY_API] = _import_thing(
        cfg[QUERY_API], 'query API', 'pytoydb.query_api')

    return cfg
