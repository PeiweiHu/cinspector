from cinspector.interfaces import CCode
from cinspector.node import CompoundStatementNode, DeclarationNode, IfStatementNode

SRC = """
int func() {
    int a = 10, b = 20;
    if ((a > 10 && b < 20) || b == 20) {
        printf();
    } else if (b < 0) {
        printf();
    } else {
        printf();
    }
}
"""


class TestCompoundStatementNode:

    def test_A(self):
        cc = CCode(SRC)
        func = cc.get_by_type_name('function_definition')[0]
        compound_statement = func.body
        assert (isinstance(compound_statement, CompoundStatementNode))
        inner_statement_lst = compound_statement.statements
        assert (len(inner_statement_lst) == 2)
        assert (isinstance(inner_statement_lst[0], DeclarationNode))
        assert (isinstance(inner_statement_lst[1], IfStatementNode))
