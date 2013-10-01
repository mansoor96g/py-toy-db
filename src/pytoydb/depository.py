# -*- coding: utf-8 -*-
"""
File: depository.py
Author: Rinat F Sabitov
Email: rinat.sabitov@gmail.com
Github: histrio
Description: simple objects store layer
"""

import pickle

from pytoydb import storage

class DepositoryException(Exception):
    pass

class Depository(object):
    """
    Хранилице комплексных объектов средствами стандартных библиотек Python.
    """

    INDEX_FILENAME = 'depository.idx'
    DEPOSIT_FILENAME = 'depository.db'

    indexmap = None

    def __init__(self):
        #в самом начале проинициализируем индекс. индексом в данном случае
        #является наш Storage, котором будем хранить записи вида:
        #(идентификатор, смещение, размер)
        idx = open(self.INDEX_FILENAME, 'ba+')
        self.dep = open(self.DEPOSIT_FILENAME, 'ba+')
        self.store = storage.Storage('LLL', idx)
        self._remap()

    def _remap(self):
        self.indexmap = {}
        for pos, (_id, offset, size) in enumerate(self.store):
            self.indexmap[_id] = pos

    def vacuum(self):
        #в процессе удаления информация о записи удаляется только в индексе,
        #что позволяет ускорить процесс, но сильно дефрагментирует данынные.
        #этод метод должен решить проблему. Д/З
        pass

    def get(self, _id):
        #получение сохраненной записи по идентификатору.
        #записи возвращаются срау в распикленном виде.
        pos = self.indexmap.get(_id)
        if pos is None:
            raise DepositoryException(
                'запись с идентификатором %s не найдена' % _id)
        _id, offset, size = self.store[pos]
        self.dep.seek(offset)
        pdata = self.dep.read(size)
        data = pickle.loads(pdata)
        return data

    def add(self, data):
        #добавление новой записи. ожидатется что на выходе будет
        #идентификатор созданной записи.
        try:
            pdata = pickle.dumps(data)
        except pickle.PicklingError as err:
            raise DepositoryException('Невозможно сохранить объект: %s' % err)
        else:
            _id = max(self.indexmap.keys() + [0,]) + 1
            offset, size = self.dep.tell(), len(pdata)
            pos = self.store.add((_id, offset, size))
            self.dep.seek(0, 2)
            self.dep.write(pdata)
            self.indexmap[_id] = pos
        return _id

    def remove(self, _id):
        # удаление записи по идентификатору. удаление происходит лишь из индекса.
        pos = self.indexmap.get(_id)
        if pos is None:
            raise DepositoryException(
                'Запись с идентификатором %s не найдена' % _id)
        self.store.remove(pos)
        self._remap()
