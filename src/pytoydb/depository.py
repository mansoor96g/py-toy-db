# -*- coding: utf-8 -*-
"""
Хранилище pickleable-объектов
"""

import pickle

from pytoydb import storage
from pytoydb.config import IO_BACKEND, IO_PURPOSE_DATA, QUERY_API


class Depository(object):
    """
    Хранилице комплексных объектов средствами стандартных библиотек Python.
    """
    indexmap = None

    def __init__(self, config):
        # в самом начале проинициализируем индекс. индексом в данном случае
        # является наш Storage, котором будем хранить записи вида:
        # (идентификатор, смещение, размер)
        self.config = config
        self.dep = self._make_buffer('data')
        self.store = storage.Storage('LLL', self._make_buffer('idx'))
        self.indexmap = {}
        self._remap()

    def _make_buffer(self, ext):
        # Возвращает новый буфер ввода-вывода, запрашивая его у IO-backend`а.
        # :ext - расширение файла
        return self.config[IO_BACKEND](
            self.config,
            IO_PURPOSE_DATA, # назначение - хранение данных
            ext
        )

    def _remap(self):
        self.indexmap = {}
        for pos, (id_, offset, size) in enumerate(self.store):
            self.indexmap[id_] = pos

    def vacuum(self):
        # в процессе удаления записи информация удаляется
        # только в карте файла, что позволяет ускорить процесс,
        # но сильно фрагментирует данынные.
        pass

    def get(self, id_):
        """
        Метод возвращает объект по идентификатору
        в исходном его (объекта) виде
        """
        # получение сохраненной записи по идентификатору.
        # записи возвращаются исходном виде.
        pos = self.indexmap.get(id_)
        if pos is None:
            raise IndexError(
                'Запись с идентификатором %s не найдена' % id_)
        id_, offset, size = self.store[pos]
        self.dep.seek(offset)
        pdata = self.dep.read(size)
        data = pickle.loads(pdata)
        return data

    def add(self, data):
        """
        Метод принимает данные для добавления
        и возвращает идентификатор созданной записи
        """
        try:
            pdata = pickle.dumps(data)
        except pickle.PicklingError as err:
            raise ValueError(
                'Невозможно сохранить объект: %s' % err)
        else:
            id_ = max(self.indexmap.keys() + [0,]) + 1
            offset, size = self.dep.tell(), len(pdata)
            pos = self.store.add((id_, offset, size))
            self.dep.seek(0, 2)
            self.dep.write(pdata)
            self.indexmap[id_] = pos
        return id_

    def remove(self, id_):
        """
        Метод удаляет объект из хранилища по идентификатору
        """
        pos = self.indexmap.get(id_)
        if pos is None:
            raise IndexError(
                'Запись с идентификатором %s не найдена' % id_)
        self.store.remove(pos)
        self._remap()


class IndexedDepository(Depository):
    """
    Индексируемое хранилище
    """
    def __init__(self, config):
        super(IndexedDepository, self).__init__(config)

        # индексы задаются конфигурацией
        index_decls = config.get('indexes')
        assert index_decls, "No indexes declared!"

        # инициализация индексов
        self.indexes = {}
        for name, cls, args in index_decls:
            self.indexes[name] = cls(config.copy(), name, *args)

    def add(self, data):
        id_ = super(IndexedDepository, self).add(data)
        for idx in self.indexes.values():
            idx.indexate(data, id_)
        return id_

    def remove(self, id_):
        super(IndexedDepository, self).remove(id_)
        for idx in self.indexes.values():
            idx.forget(id_)

    @property
    def query(self):
        """
        Возвращает query-объект,
        API которого зависит от конфигурации
        """
        return self.config[QUERY_API](self)


import threading
import Queue

class ThreadsafeDepository(threading.Thread):

    TASK_ADD, TASK_DELETE, TASK_REPLACE, TASK_GET = range(1,5)

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        self.queue = Queue.Queue(5)
        self.dep = Depository(*args, **kwargs)

    def run(self):
        while True:
            task = self.queue.get()
            self.process(task)
            self.queue.task_done()


    def add(self, data, wait=False):
        container = Queue.Queue(1)
        task = {
            "args":(data, ),
            "task":self.TASK_ADD,
            "container":container
        }
        if wait:
            lock = threading.Lock()
            task['lock']=lock
        self.queue.put(task)
        if wait:
            lock.acquire()
            return container.get()


    def process(self, task):

        import time
        time.sleep(2)

        task_type = task['task']
        if task_type == self.TASK_ADD:
            result = self.dep.add(*task['args'])
            task['container'].put(result)
            print task
            if 'lock' in task:
                task['lock'].release()
        elif task_type == self.TASK_REMOVE:
            result = self.dep.remove(*task['args'])
        elif task_type == self.TASK_REPLACE:
            result = self.dep.replace(*task['args'])
        elif task_type == self.TASK_GET:
            result = self.dep.get(*task['args'])
