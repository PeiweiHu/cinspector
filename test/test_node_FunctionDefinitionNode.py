from cinspector.interfaces import CCode
from cinspector.nodes import FunctionDefinitionNode, ParameterListNode, IdentifierNode

SRC = """
static inline int func(int a, struct st ins, struct st **ins_pointer, struct st *ins_pointer_arr[]) {
    return 0;
}

int foo(int (*func_pointer)(const static int *)) {
    return 0;
}

int (*bar(int (*cmp)(void *)))(int) {
    return 0;
}
"""


class TestFunctionDefinitionNode:

    def test_func(self):
        cc = CCode(SRC)
        func = cc.get_by_type_name('function_definition')

        # test the property name
        func = [_ for _ in func if _.name.src == 'func'][0]
        assert (isinstance(func, FunctionDefinitionNode))
        # test the property inline and static
        assert (func.inline and func.static)
        # test the property parameters
        func_parameters = func.parameters
        assert (isinstance(func_parameters, ParameterListNode))
        para_decl_lst = func_parameters.children
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
        # test the property name
        foo = [_ for _ in foo if _.name.src == 'foo'][0]
        # test the property parameters
        # int (*func_pointer)(const static int *)
        para_decl1 = foo.parameters.children[0]
        assert (para_decl1.name.src == 'func_pointer')
        assert (para_decl1.src == 'int (*func_pointer)(const static int *)')

    def test_bar(self):
        cc = CCode(SRC)
        bar = cc.get_by_type_name('function_definition')
        # test the property name
        bar = [_ for _ in bar if _.name.src == 'bar'][0]

        # int (*cmp)(void *)
        para_decl = bar.parameters.children[0]
        assert (para_decl.src == 'int (*cmp)(void *)')
