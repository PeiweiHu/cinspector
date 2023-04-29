from cinspector.interfaces import CCode
from cinspector.nodes import StructSpecifierNode, FieldDeclarationListNode, FieldDeclarationNode, BasicNode, FieldIdentifierNode
from cinspector.nodes import Util

SRC = """
struct st {
    int a;
    struct {
        int *b;
        int c[];
    };
};
"""


class TestStructSpecifierNode:

    def test_A(self):
        cc = CCode(SRC)
        struct = cc.get_by_type_name('struct_specifier')
        assert (len(struct) == 2)
        struct = Util.sort_nodes(struct)
        struct = struct[0]
        assert (isinstance(struct, StructSpecifierNode))

        decl_lst = struct.body
        assert (isinstance(decl_lst, FieldDeclarationListNode))
        decl_lst = decl_lst.children
        assert (len(decl_lst) == 2)
        decl_lst = Util.sort_nodes(decl_lst)
        int_a = decl_lst[0]
        assert (isinstance(int_a, FieldDeclarationNode))
        assert (int_a.type.src == 'int')
        assert (int_a.declarator.src == 'a')
        assert (isinstance(int_a.declarator, FieldIdentifierNode))
        struct_anonymous = decl_lst[1]
        assert (isinstance(struct_anonymous, FieldDeclarationNode))
        assert (isinstance(struct_anonymous.type, StructSpecifierNode))
        assert (struct_anonymous.declarator is None)

        # test Query for StructSpecifierNode
        struct_st = cc.get_by_type_name_and_query('struct_specifier',
                                                  {'type_identifier': 'st'})[0]
        assert (isinstance(struct_st, StructSpecifierNode))
        assert (struct_st.name.src == 'st')
