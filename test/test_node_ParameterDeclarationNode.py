from cinspector.interfaces import CCode
from cinspector.nodes import ParameterDeclarationNode, IdentifierNode, TypeQualifierNode, StorageClassSpecifierNode

SRC = """
int func(int a, struct st ins, struct st **ins_pointer, struct st *ins_pointer_arr[]) {
    return 0;
}

int foo(int (*func_pointer)(const static int *)) {
    return 0;
}

int (*bar(int (*cmp)(void *)))(int) {
    return 0;
}
"""


class TestParameterDeclarationNode:

    def test_func(self):
        cc = CCode(SRC)
        func = cc.get_by_type_name('function_definition')
        func = [_ for _ in func if _.name.src == 'func'][0]
        para_decl_lst = func.descendants_by_type_name('parameter_declaration')
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

    def test_foo(self):
        cc = CCode(SRC)
        foo = cc.get_by_type_name('function_definition')
        foo = [_ for _ in foo if _.name.src == 'foo'][0]

        # int (*func_pointer)(const static int *)
        para_decl1 = foo.child_by_field_name('declarator').child_by_field_name(
            'parameters').children[0]
        assert (para_decl1.name.src == 'func_pointer')

        # const static int *
        para_decl2 = para_decl1.child_by_field_name(
            'declarator').child_by_field_name('parameters').children[0]
        assert (para_decl2.name is None)
        assert (para_decl2.type_qualifier[0].src == 'const')
        assert (para_decl2.storage_class_specifier[0].src == 'static')

    def test_bar(self):
        cc = CCode(SRC)
        bar = cc.get_by_type_name('function_definition')
        bar = [_ for _ in bar if _.name.src == 'bar'][0]

        # int (*bar(int (*cmp)(void *)))(int)
        para_decl_lst = bar.descendants_by_type_name('parameter_declaration')
        for _decl in para_decl_lst:
            if _decl.src == 'int (*cmp)(void *)':
                assert (_decl.name.src == 'cmp')
            elif _decl.src == 'void *':
                assert (_decl.name is None)
            elif _decl.src == 'int':
                assert (_decl.name is None)
            else:
                assert (0)
