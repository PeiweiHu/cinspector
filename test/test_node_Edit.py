from cinspector.interfaces import CCode
from cinspector.nodes import Edit, FunctionDefinitionNode, EditPos, edit_str

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
        assert (len(func.descendants_by_type_name('call_expression')) == 1)
        """
        expression_statement - b(0);
        call_expression - b(0) # without ;
        """
        call_exp = func.descendants_by_type_name('expression_statement')[0]
        func_edit = Edit(func)
        new_func = func_edit.remove_child(call_exp)
        assert (new_func.node_type == 'function_definition')
        assert (new_func.descendants_by_type_name('call_expression') == [])

    def test_edit_str(self):
        s = "012345678"
        edits = []
        edits.append(EditPos(1, 3, "a"))
        edits.append(EditPos(5, 6, "bcd"))
        s = edit_str(s, edits)
        assert (s == '0a34bcd678')

        s = "012345678"
        edits = []
        edits.append(EditPos(0, 30, "a"))
        s = edit_str(s, edits)
        assert (s == None)

        s = "012345678"
        edits = []
        edits.append(EditPos(0, 4, "a"))
        edits.append(EditPos(1, 4, "a"))
        s = edit_str(s, edits)
        assert (s == None)
