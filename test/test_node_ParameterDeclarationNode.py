from cinspector.interfaces import CCode
from cinspector.nodes import ParameterDeclarationNode, IdentifierNode

SRC = """
int func(int a, struct st ins, struct st **ins_pointer, struct st *ins_pointer_arr[]) {
    return 0;
}
"""


class TestParameterDeclarationNode:

    def test_A(self):
        cc = CCode(SRC)
        para_decl_lst = cc.get_by_type_name('parameter_declaration')
        # number of the parameter
        assert (len(para_decl_lst) == 4)

        # the first parameter - int a
        para0 = para_decl_lst[0]
        assert (str(para0.type.src) == 'int')
        assert (isinstance(para0.name, IdentifierNode))
        assert (str(para0.name.src) == 'a')

        # the second parameter - struct st ins
        para1 = para_decl_lst[1]
        assert (str(para1.type.src) == 'struct st')
        assert (isinstance(para1.name, IdentifierNode))
        assert (str(para1.name.src) == 'ins')

        # the third parameter - struct st **ins_pointer
        para2 = para_decl_lst[2]
        assert (str(para2.type.src) == 'struct st')
        assert (isinstance(para2.name, IdentifierNode))
        assert (str(para2.name.src) == 'ins_pointer')

        # the forth parameter - struct st *ins_pointer_arr[]
        para3 = para_decl_lst[3]
        assert (str(para3.type.src) == 'struct st')
        assert (isinstance(para3.name, IdentifierNode))
        assert (str(para3.name.src == 'ins_pointer_arr'))
