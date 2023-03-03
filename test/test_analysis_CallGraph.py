import sys

from cinspector.interfaces import CCode
from cinspector.analysis import CallGraph
from cinspector.nodes import CompoundStatementNode, DeclarationNode, IfStatementNode

SRC = """
void a(int p) {
    b(0);
}

void b(int p) {
    c(1, 2);
}

void c(int p1, int p2) {
    a(0);
}

void d() {
    b(1);
    c(1, 2);
}

void e() {}
"""


def get_func(name, funcs):
    for _ in funcs:
        if _.name.src == name:
            return _
    return None


class TestCallGraph:

    def test_A(self):
        cc = CCode(SRC)
        funcs = cc.get_by_type_name('function_definition')
        fa = get_func('a', funcs)
        fb = get_func('b', funcs)
        fc = get_func('c', funcs)
        fd = get_func('d', funcs)
        fe = get_func('e', funcs)
        assert (fa and fb and fc and fd and fe)
        cg = CallGraph(funcs).analysis()
        assert (len(cg.nodes) == 5)
        assert (cg.has_edge(fa, fb))
        assert (cg.has_edge(fb, fc))
        assert (cg.has_edge(fc, fa))
        assert (cg.has_edge(fd, fb))
        assert (cg.has_edge(fd, fc))
        assert (cg.has_node(fe))
