from cinspector.interfaces import CCode
from cinspector.nodes import ParenthesizedExpressionNode

SRC = """
int a = 10, b = 20;
if (a > 10) {
    printf("%d\n", a);
}
if ((a > 10 && b < 20) || b == 20) {
    printf();
}
"""


class TestParenthesizedExpressionNode:

    def test_A(self):
        cc = CCode(SRC)
        pe = cc.get_by_type_name('parenthesized_expression')
        assert (len(pe) == 3)
        for _ in pe:
            if _.src == '(a > 10)':
                assert (_.remove_parenthese().src == 'a > 10')
            elif _.src == '((a > 10 && b < 20) || b == 20)':
                assert (_.remove_parenthese().src ==
                        '(a > 10 && b < 20) || b == 20')
            elif _.src == '(a > 10 && b < 20)':
                assert (_.remove_parenthese().src == 'a > 10 && b < 20')
            else:
                assert (False)
