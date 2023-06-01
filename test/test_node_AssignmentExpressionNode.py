from cinspector.interfaces import CCode
from cinspector.nodes import AssignmentExpressionNode, Util

SRC = """
void funcA() {
    int a, b, c = 1;
    a = b;
    b += c;
    c |= a;
}
"""


class TestAssignmentNode:

    def test_A(self):
        cc = CCode(SRC)
        # locate funcA
        assignmment_exps = cc.get_by_type_name('assignment_expression')
        assignmment_exps = Util.sort_nodes(assignmment_exps)
        assert (assignmment_exps[0].symbol == '=')
        assert (assignmment_exps[1].symbol == '+=')
        assert (assignmment_exps[2].symbol == '|=')
