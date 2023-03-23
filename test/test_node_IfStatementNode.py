from cinspector.interfaces import CCode
from cinspector.nodes import IfStatementNode, BasicNode

SRC = """
int a = 10, b = 20;
if ((a > 10 && b < 20) || b == 20) {
    printf();
} else if (b < 0) {
    printf();
} else {
    printf();
}
"""


class TestIfStatementNode:

    def test_A(self):
        cc = CCode(SRC)
        if_stmts = cc.get_by_type_name('if_statement')
        assert (len(if_stmts) == 2)  # <if> and <else if> in SRC
        if_stmts = BasicNode.sort_nodes(if_stmts)

        stmt0 = if_stmts[0]
        assert (isinstance(stmt0, IfStatementNode))
        # test condition
        assert (stmt0.condition.src == '((a > 10 && b < 20) || b == 20)')
        # test consequence
        assert (stmt0.consequence.type == 'compound_statement')
        # test alternative
        assert (stmt0.alternative.type == 'if_statement')
        assert (isinstance(stmt0.alternative, IfStatementNode))
        # test entry_constraints
        # the constraint should be [[a > 10, b < 20], [b == 20]]
        constraints = stmt0.entry_constraints()
        assert (len(constraints) == 2)
        for _ in constraints:
            if (len(_) == 2):
                assert ('a > 10' in str(_))
                assert ('b < 20' in str(_))
            elif (len(_) == 1):
                assert ('b == 20' in str(_))
            else:
                assert (False)
