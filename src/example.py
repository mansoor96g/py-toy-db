# -*- coding: utf-8 -*-

from pytoydb.depository import IndexedDepository
from pytoydb.index import HashIndex
from pytoydb.config import configure


if __name__ == '__main__':
    dep = IndexedDepository(
        configure(
            #io_backend='files',
            #base_name='depository',
            indexes=(
                ('a', HashIndex, (lambda x: x.get('a'),)),
                ('b', HashIndex, (lambda x: x.get('b'),))
            )
        ))

    # раскомментить при работе с io_backend='files'
    # if not list(dep.query):
    if True:
        dep.add({'a': 1, 'b': 101})
        dep.add({'a': 2, 'b': 102, 'c': 456, 2: 4})
        dep.add({'a': 1, 'b': 103})
        dep.add({'a': 3})
        dep.add({'a': 2, 'b': 101, 101: 'b'})

    from pprint import pprint

    def show(title, query):
        print title
        pprint(list(query))
        print

    show('all', dep.query)

    show('a = 1', dep.query('a', 1))

    show('a = 2', dep.query('a', 2))

    show('b = 101', dep.query('b', 101))

    show('a = 2, b = 101',
        dep.query('a', 2)('b', 101))

    dep.remove(5)

    show('a = 2, b = 101',
        dep.query('a', 2)('b', 101))
