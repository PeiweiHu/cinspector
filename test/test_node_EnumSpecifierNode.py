import sys

sys.path.append('..')
from cinspector.interfaces import CCode
from cinspector.nodes import EnumSpecifierNode, IdentifierNode, NumberLiteralNode

SRC = """
#include "stdio.h"


#define MACRO1 1
#define MACRO2 2

enum A {A1};

enum B {
    B1,
    B2
};

enum C {
    C1 = 3,
    C2,
    C3
};


enum D {
    D1,
    D2 = -1,
    D3,
    D4 = 4,
    D5,
};

enum E {
    E1,
    E2 = MACRO1,
    E3 = 3,
    E4 = MACRO2
};

"""


class TestEnumSpecifierNode:

    def test_A(self):
        cc = CCode(SRC)
        enum = cc.get_enum('A')
        assert (len(enum) == 1)
        enum = enum[0]
        assert (isinstance(enum, EnumSpecifierNode))
        assert (len(enum.unsolved_value()) == 0)
        # test EnumSpecifierNode.kv
        value_dic = enum.kv
        assert (len(value_dic) == 1)
        k = list(value_dic)[0]
        assert (k.src == 'A1')
        assert (value_dic[k] is None)
        # test EnumSpecifierNode.conclude_value()
        value_dic = enum.conclude_value()
        assert (len(value_dic) == 1)
        k = list(value_dic)[0]
        assert (k.src == 'A1')
        assert (value_dic[k] == 0)

    def test_B(self):
        cc = CCode(SRC)
        enum = cc.get_enum('B')
        assert (len(enum) == 1)
        enum = enum[0]
        # test EnumSpecifierNode.kv
        for _k, _v in enum.kv.items():
            assert (_v is None)
        # test EnumSpecifierNode.conclude_value()
        for _k, _v in enum.conclude_value().items():
            if _k.src == 'B1':
                assert (_v == 0)
            elif _k.src == 'B2':
                assert (_v == 1)

    def test_C(self):
        cc = CCode(SRC)
        enum = cc.get_enum('C')
        assert (len(enum) == 1)
        enum = enum[0]
        # test EnumSpecifierNode.kv
        for _k, _v in enum.kv.items():
            if _k.src == 'C1':
                assert (isinstance(_v, NumberLiteralNode))
                assert (_v.src == '3')
            else:
                assert (_v is None)
        # test EnumSpecifierNode.conclude_value()
        for _k, _v in enum.conclude_value().items():
            if _k.src == 'C1':
                assert (_v == 3)
            elif _k.src == 'C2':
                assert (_v == 4)
            elif _k.src == 'C3':
                assert (_v == 5)
            else:
                assert (False)

    def test_D(self):
        cc = CCode(SRC)
        enum = cc.get_enum('D')
        assert (len(enum) == 1)
        enum = enum[0]
        # test EnumSpecifierNode.kv
        for _k, _v in enum.kv.items():
            if _k.src == 'D2':
                assert (isinstance(_v, NumberLiteralNode))
                assert (_v.src == '-1')
            elif _k.src == 'D4':
                assert (isinstance(_v, NumberLiteralNode))
                assert (_v.src == '4')
            else:
                assert (_v is None)
        # test EnumSpecifierNode.conclude_value()
        for _k, _v in enum.conclude_value().items():
            if _k.src == 'D1':
                assert (_v == 0)
            elif _k.src == 'D2':
                assert (_v == -1)
            elif _k.src == 'D3':
                assert (_v == 0)
            elif _k.src == 'D4':
                assert (_v == 4)
            elif _k.src == 'D5':
                assert (_v == 5)
            else:
                assert (False)

    def test_E(self):
        cc = CCode(SRC)
        enum = cc.get_enum('E')
        assert (len(enum) == 1)
        enum = enum[0]
        # test EnumSpecifierNode.kv
        for _k, _v in enum.kv.items():
            if _k.src == 'E2':
                assert (isinstance(_v, IdentifierNode))
                assert (_v.src == 'MACRO1')
            elif _k.src == 'E3':
                assert (isinstance(_v, NumberLiteralNode))
                assert (_v.src == '3')
            elif _k.src == 'E4':
                assert (isinstance(_v, IdentifierNode))
                assert (_v.src == 'MACRO2')
            else:
                assert (_v is None)
        # test unsolved_value
        unsolved = enum.unsolved_value()
        assert (len(unsolved) == 2)
        for _ in unsolved:
            assert (isinstance(_, IdentifierNode))
            assert (_.src == 'MACRO1' or _.src == 'MACRO2')
        # test EnumSpecifierNode.conclude_value()
        for _k, _v in enum.conclude_value().items():
            if _k.src == 'E1':
                assert (_v == 0)
            elif _k.src == 'E2':
                assert (_v is None)
            elif _k.src == 'E3':
                assert (_v == 3)
            elif _k.src == 'E4':
                assert (_v is None)
            else:
                assert (False)
        # test EnumSpecifierNode.conclude_value() with value_dic
        val_dic = dict()
        for _ in unsolved:
            if _.src == 'MACRO1':
                val_dic[_] = 1
            elif _.src == 'MACRO2':
                val_dic[_] = 2
            else:
                assert (False)
        for _k, _v in enum.conclude_value(val_dic).items():
            if _k.src == 'E1':
                assert (_v == 0)
            elif _k.src == 'E2':
                assert (_v == 1)
            elif _k.src == 'E3':
                assert (_v == 3)
            elif _k.src == 'E4':
                assert (_v == 2)
            else:
                assert (False)
