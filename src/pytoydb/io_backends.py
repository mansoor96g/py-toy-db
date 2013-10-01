# -*- coding: utf-8 -*-
"""
Backend`ы ввода-вывода
"""
import io

from pytoydb.config import BASE_NAME


def memory(config, purpose, name):
    """
    backend, хранящий все виды информации в памяти
    """
    return io.BytesIO()


def files(config, purpose, name):
    """
    backend, хранящий все виды информации на диске
    """
    return open('%s.%s' % (config[BASE_NAME], name), 'a+b')
