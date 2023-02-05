import sys
sys.path.append('..')
from cinspector.interfaces import CCode
from cinspector.nodes import PreprocDefNode, IdentifierNode, PreprocArgNode


SRC = """

#define MACRO1 1
#define MACRO2 MACRO1

"""


class TestPreprocDefNode:
    def test_preproc_def(self):
        cc = CCode(SRC)
        macro_lst = cc.get_by_type_name('preproc_def')
        assert(len(macro_lst) == 2)
        for _ in macro_lst:
            assert(isinstance(_, PreprocDefNode))
            assert(isinstance(_.name, IdentifierNode))
            assert(isinstance(_.value, PreprocArgNode))
            if _.name.src == 'MACRO1':
                assert(_.value.src == '1')
            elif _.name.src == 'MACRO2':
                assert(_.value.src == 'MACRO1')
            else:
                assert(False)
