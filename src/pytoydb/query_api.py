# -*- coding: utf-8 -*-
"""
API для формирования запросов к хранилищу
"""

class Simple(object):
    """
    Простейший API
    Запросы выглядят примерно так: data.query('a', 1)('b', 2)
    """

    def __init__(self, dep, steps=None):
        self._dep = dep
        self._steps = steps or []

    def __call__(self, name, *args, **kwargs):
        return self.__class__(
            self._dep,
            self._steps + [(name, args, kwargs)]
        )

    def __iter__(self):
        if not self._steps:
            ids = self._dep.indexmap.keys()
        else:
            def do((n, args, kwargs)):
                return self._dep.indexes[n].query(*args, **kwargs)

            ids = set(do(self._steps[0]))

            for s in self._steps[1:]:
                ids.intersection_update(do(s))

        for i in ids:
            yield i, self._dep.get(i)
