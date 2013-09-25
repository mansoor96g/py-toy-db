# -*- coding: utf-8 -*-
"""
Хранилище структурированных гомогенных данных
"""

import struct
import io


class Storage(object):
    """
    Хранилище гомогенных данных в компактной форме
    """
    def __init__(self, fmt, buff):
        """
        Метод конструирует хранилище данных
        указанного формата :fmt (строка формата struct)
        в указанном буфере :buff
        """
        self._struct = struct.Struct(fmt)
        self._io = buff
        self._size = 0

    @property
    def _pos(self):
        # возвращает индекс текущего элемента в буфере
        return self._io.tell() // self._struct.size

    @_pos.setter
    def _pos(self, val):
        # перемещает текущую позицию в буфере к указанному элементу
        if val != self._pos:
            if val >= len(self) or val < 0:
                raise IndexError('Index out of range!')
            self._io.seek(self._struct.size * val)

    def __len__(self):
        """
        Метод возвращает длину контейнера в элементах
        """
        return self._size

    def add(self, data):
        """
        Метод добавляет кортеж данных в хранилище и возвращает
        индекс добавленного элемента
        """
        val = self._struct.pack(*data)
        self._io.seek(0, 2)
        pos = self._io.tell() // self._struct.size
        self._io.write(val)
        self._size = pos + 1
        return pos

    def remove(self, idx):
        """
        Метод удаляет элемент по индексу
        """
        if (len(self) - idx) > 1:
            self._pos = idx + 1
            rest = self._io.read()
        else:
            rest = None

        self._pos = idx
        self._io.truncate()

        if rest is not None:
            self._io.write(rest)

        self._size = self._io.tell() // self._struct.size

    def __getitem__(self, idx):
        """
        Метод возвращает элемент по индексу
        """
        self._pos = idx
        return self._struct.unpack(
            self._io.read(self._struct.size))

    def __setitem__(self, idx, data):
        """
        Метод заменяет элемент по индексу указанными данными
        """
        self._pos = idx
        self._io.write(self._struct.pack(*data))

    def __iter__(self):
        """
        Метод возвращает iterable по имеющимся элементам
        """
        self._pos = 0
        while True:
            val = self._io.read(self._struct.size)
            if len(val) < self._struct.size:
                break
            yield self._struct.unpack(val)


if __name__ == '__main__':
    store = Storage('LL?', io.BytesIO())

    print "-- create --"
    ids = [store.add((x, 10 - x, x % 2 == 0)) for x in xrange(10)]
    print list(store)

    print "-- select --"
    for i in ids[-1:0:-2]:
        print 'store[%d] =>' % i, store[i]

    print "-- remove --"
    store.remove(1)
    store.remove(2)
    store.remove(3)
    store.remove(4)
    store.remove(5)
    print list(store)

    print "-- replace --"
    store[0] = (10000, 10000, False)
    print list(store)
