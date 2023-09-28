from cinspector.interfaces import CCode

SRC = """
    int a, b, c = 1;
    int d;
    int e;
"""

SRC1 = """
void BND_Fixup(void) {
  if (((byte)prefixes & 2)) {
    *(undefined4 *)(all_prefixes + (long)last_repnz_prefix * 4) = 0x4f2;
  }
}
"""


class TestTokenize:

    def test_A(self):
        cc = CCode(SRC)
        tokens = cc.node.tokenize()
        tokens = [_.src for _ in tokens]
        assert tokens == [
            'int', 'a', ',', 'b', ',', 'c', '=', '1', ';', 'int', 'd', ';',
            'int', 'e', ';'
        ]

    def test_B(self):
        cc = CCode(SRC1)
        tokens = cc.node.tokenize()
        tokens = [_.src for _ in tokens]
        assert tokens == [
            'void', 'BND_Fixup', '(', 'void', ')', '{', 'if', '(', '(', '(',
            'byte', ')', 'prefixes', '&', '2', ')', ')', '{', '*', '(',
            'undefined4', '*', ')', '(', 'all_prefixes', '+', '(', 'long', ')',
            'last_repnz_prefix', '*', '4', ')', '=', '0x4f2', ';', '}', '}'
        ]
