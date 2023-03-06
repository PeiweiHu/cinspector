from cinspector.interfaces import CCode
from cinspector.node import BasicNode

SRC = """
    int a, b, c = 1;
    int d;
    int e;
"""


class TestSort:

    def test_A(self):
        cc = CCode(SRC)
        decls = cc.get_by_type_name('declaration')
        assert (len(decls) == 3)

        ids = []
        for _d in decls:
            ids += _d.declared_identifiers()

        id_dic = dict()
        for _id in ids:
            id_dic[_id.src] = _id
        for _ in ['a', 'b', 'c', 'd', 'e']:
            assert (_ in id_dic.keys())

        lst = [id_dic['b'], id_dic['e'], id_dic['c'], id_dic['a'], id_dic['d']]
        ascending = BasicNode.sort_nodes(lst)
        assert (ascending[0].src == 'a')
        assert (ascending[1].src == 'b')
        assert (ascending[2].src == 'c')
        assert (ascending[3].src == 'd')
        assert (ascending[4].src == 'e')
        descending = BasicNode.sort_nodes(lst, reverse=True)
        assert (descending[4].src == 'a')
        assert (descending[3].src == 'b')
        assert (descending[2].src == 'c')
        assert (descending[1].src == 'd')
        assert (descending[0].src == 'e')
