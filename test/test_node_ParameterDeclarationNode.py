import sys

sys.path.append('..')
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
        assert (not para0.type.is_pointer())
        assert (not para0.type.is_array())
        assert (isinstance(para0.name, IdentifierNode))
        assert (str(para0.name.src) == 'a')

        # the second parameter - struct st ins
        para1 = para_decl_lst[1]
        assert (str(para1.type.src) == 'struct st')
        assert (not para1.type.is_pointer())
        assert (not para1.type.is_array())
        assert (isinstance(para1.name, IdentifierNode))
        assert (str(para1.name.src) == 'ins')

        # the third parameter - struct st **ins_pointer
        para2 = para_decl_lst[2]
        assert (str(para2.type.src) == 'struct st')
        assert (para2.type.is_pointer())
        assert (para2.type.pointer_level == 2)
        assert (not para2.type.is_array())
        assert (isinstance(para2.name, IdentifierNode))
        assert (str(para2.name.src) == 'ins_pointer')

        # the forth parameter - struct st *ins_pointer_arr[]
        para3 = para_decl_lst[3]
        assert (str(para3.type.src) == 'struct st')
        assert (para3.type.is_pointer())
        assert (para3.type.pointer_level == 1)
        assert (para3.type.is_array())
        assert (para3.type.array_level == 1)
        assert (isinstance(para3.name, IdentifierNode))
        assert (str(para3.name.src == 'ins_pointer_arr'))
