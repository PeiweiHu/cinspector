from cinspector.interfaces import CCode
from cinspector.nodes import Edit, FunctionDefinitionNode

SRC = """
void a(int p) {
    int b = 1;
    b(0);
}
"""


class TestEdit:

    def test_A(self):
        cc = CCode(SRC)
        func = cc.get_by_type_name('function_definition')[0]
        assert (len(func.children_by_type_name('call_expression')) == 1)
        """
        expression_statement - b(0);
        call_expression - b(0) # without ;
        """
        call_exp = func.children_by_type_name('expression_statement')[0]
        func_edit = Edit(func)
        new_func = func_edit.remove_child(call_exp)
        assert (new_func.node_type == 'function_definition')
        assert (new_func.children_by_type_name('call_expression') == [])
