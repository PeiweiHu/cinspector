from cinspector.interfaces import CCode
from cinspector.nodes import IdentifierNode, DeclarationNode, FunctionDefinitionNode, Util

SRC = """
void funcA() {
    int a, b, c = 1;
}

void funcB() {
    struct STy ins, *ins_pointer, ins_arr[c];
}

pcap_t *pcap_open_rpcap(const char *source, int snaplen, int flags,
    int read_timeout, struct pcap_rmtauth *auth, char *errbuf);
"""


class TestDeclarationNode:

    def test_A(self):
        cc = CCode(SRC)
        # locate funcA
        funcs = cc.get_by_type_name('function_definition')
        for _f in funcs:
            if _f.name.src == 'funcA':
                funcA = _f
        assert (funcA)
        # test
        declarations = funcA.children_by_type_name('declaration')
        assert (len(declarations) == 1)
        declaration = declarations[0]
        assert (isinstance(declaration, DeclarationNode))
        assert (declaration.type.src == 'int')
        declarator = declaration.declarator
        assert (len(declarator) == 3)
        # test declared_identifiers
        ids = declaration.declared_identifiers()
        assert (len(ids) == 3)
        for _ in ids:
            assert (_.src in ['a', 'b', 'c'])

    def test_B(self):
        cc = CCode(SRC)
        # locate funcA
        funcs = cc.get_by_type_name('function_definition')
        for _f in funcs:
            if _f.name.src == 'funcB':
                funcB = _f
        assert (funcB)
        # test
        declarations = funcB.children_by_type_name('declaration')
        assert (len(declarations) == 1)
        declaration = declarations[0]
        assert (isinstance(declaration, DeclarationNode))
        assert (declaration.type.src == 'struct STy')
        declarator = declaration.declarator
        assert (len(declarator) == 3)
        # test declared_identifiers
        ids = declaration.declared_identifiers()
        assert (len(ids) == 3)
        for _ in ids:
            assert (_.src in ['ins', 'ins_pointer', 'ins_arr'])

    def test_C(self):
        # test function declarator in declaration
        cc = CCode(SRC)
        decls = cc.get_by_type_name('declaration')
        decls = Util.sort_nodes(decls)
        pcap_decl = decls[-1]
        assert (pcap_decl.declared_identifiers()[0].src == 'pcap_open_rpcap')
