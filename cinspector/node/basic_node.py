from functools import cmp_to_key
from typing import List, Optional, Dict, Iterable
from .node import Node, Util


class BasicNode(Node, Util):

    def __init__(self, src: str, ts_node=None) -> None:
        self.internal_src = src
        """
        Ideally, the following condtion is true only when file content is
        passed to BasicNode. Other nodes such as FunctionDefinitionNode
        should be initialized with ts_node dictated.
        """
        if not ts_node:
            ts_node = self.get_tree(src).root_node
        self.internal = ts_node
        self.type = ts_node.type
        self.ts_type = ts_node.type
        self._parent = None
        self.start_point = ts_node.start_point
        self.end_point = ts_node.end_point
        self.child_count = ts_node.child_count
        self._children = None
        self.src = self.get_node_raw(self.internal_src, ts_node)

    @property
    def children(self):
        """
        DO NOT use this attribute on huge BasicNode such as ndoe
        of file, otherwise horrible recursion.
        """
        if not self._children:
            self._children = [
                self.make_wrapper(_ch)
                for _ch in self.internal.children
                if _ch.type not in ['(', ')', ',', ';', '{', '}']
            ]
        return self._children

    def __str__(self) -> str:
        # return f'({self.type}){self.src}'
        return self.src

    def __repr__(self) -> str:
        # return f'({self.__hash__}){self.src}'
        return self.src

    def equal(self, __o) -> bool:
        is_node = isinstance(__o, BasicNode)
        internal_src_eq = (self.internal_src == __o.internal_src)
        position_eq = (self.internal.start_point == __o.internal.start_point)
        position_eq = position_eq and (self.internal.end_point
                                       == __o.internal.end_point)
        return is_node and internal_src_eq and position_eq

    @property
    def parent(self):
        if not self._parent:
            self._parent = self.make_wrapper(self.internal.parent)
        return self._parent

    def in_front(self, node):
        return self.start_point[0] < node.start_point[0] or \
            (self.start_point[0] == node.start_point[0] and self.start_point[1] < node.start_point[1])

    @staticmethod
    def sort_nodes(nodes: Iterable, reverse: bool = False) -> Iterable:
        """ Sort the instances of BasicNode by their position in source code

        Args:
            nodes (Iterable): nodes waiting for sorting
            reverse (bool=False): use descending instead of ascending

        Return:
            sorted Iterable object
        """

        def cmp_position(node1: BasicNode, node2: BasicNode) -> int:
            if node1.start_point[0] < node2.start_point[0] or \
                    (node1.start_point[0] == node2.start_point[0] and node1.start_point[1] < node2.start_point[1]):
                return -1
            else:
                return 1

        sorted_nodes = sorted(nodes,
                              key=cmp_to_key(cmp_position),
                              reverse=reverse)
        return sorted_nodes

    def make_wrapper(self, ts_node):
        if not ts_node:
            return None
        wrapper_dict = {
            'function_definition': FunctionDefinitionNode,
            'expression_statement': ExpressionStatementNode,
            'call_expression': CallExpressionNode,
            'type_identifier': TypeNode,
            'primitive_type': TypeNode,
            'if_statement': IfStatementNode,
            'parenthesized_expression': ParenthesizedExpressionNode,
            'for_statement': ForStatementNode,
            'while_statement': WhileStatementNode,
            'assignment_expression': AssignmentExpressionNode,
            'init_declarator': InitDeclaratorNode,
            'return_statement': ReturnStatementNode,
            'binary_expression': BinaryExpressionNode,
            'conditional_expression': ConditionalExpressionNode,
            'cast_expression': CaseExpressionNode,
            'identifier': IdentifierNode,
            'unary_expression': UnaryExpressionNode,
            'subscript_expression': SubscriptExpressionNode,
            'number_literal': NumberLiteralNode,
            'sized_type_specifier': TypeNode,
            'macro_type_specifier': TypeNode,
            'struct_specifier': TypeNode,
            'declaration': DeclarationNode,
            'preproc_function_def': PreprocFunctionDefNode,
            'preproc_def': PreprocDefNode,
            'preproc_arg': PreprocArgNode,
            'enum_specifier': EnumSpecifierNode,
            'enumerator_list': EnumeratorListNode,
            'enumerator': EnumeratorNode,
            'parameter_declaration': ParameterDeclarationNode,
            'variadic_parameter': VariadicParameterNode,
            'compound_statement': CompoundStatementNode,
        }
        init_func = wrapper_dict[
            ts_node.type] if ts_node.type in wrapper_dict.keys() else BasicNode
        return init_func(self.internal_src, ts_node)

    def child_by_field_name(self, name):
        assert (type(name) == str)
        return self.make_wrapper(self.internal.child_by_field_name(name))

    def children_by_type_name(self, name):
        if type(name) == str:
            name = [name]
        node_lst = []
        cursor = self.internal.walk()
        while True:
            if cursor.node.type in name:
                node_lst.append(self.make_wrapper(cursor.node))
            if not cursor.goto_first_child():
                while not cursor.goto_next_sibling():
                    if not cursor.goto_parent():
                        return node_lst


# currently only add commonly used type
class TypeNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.pointer_level = 0
        self.array_level = 0

    def is_pointer(self):
        return self.pointer_level != 0

    def is_array(self):
        return self.array_level != 0


class WhileStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.condition = self.child_by_field_name('condition')
        if self.children:
            self.body = self.children[-1]
        else:
            self.body = None


class IdentifierNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)

    def __eq__(self, obj):
        return super().__eq__(obj)

    def __hash__(self):
        return super().__hash__()


class CaseExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.type = self.child_by_field_name('type')
        self.value = self.child_by_field_name('value')


class UnaryExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.argument = self.child_by_field_name('argument')

    def used_ids(self):
        ids = self.children_by_type_name('identifier')
        return ids


class ConditionalExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.condition = self.child_by_field_name('condition')
        self.consequence = self.child_by_field_name('consequence')
        self.alternative = self.child_by_field_name('alternative')


class NumberLiteralNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)


class ReturnStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.value = self.children[1] if len(self.children) > 1 else None


class PreprocFunctionDefNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.name = self.child_by_field_name('name')
        self.parameters = self.child_by_field_name('parameters')
        self.value = self.child_by_field_name('value')


class ForStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.initializer = self.child_by_field_name('initializer')
        self.condition = self.child_by_field_name('condition')
        self.update = self.child_by_field_name('update')
        if self.children:
            self.body = self.children[-1]
        else:
            self.body = None


class BinaryExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.left = self.child_by_field_name('left')
        self.right = self.child_by_field_name('right')
        self.symbol = self.get_raw(self.internal_src, self.left.end_point,
                                   self.right.start_point).strip()

    def is_logic_op(self):
        if self.symbol in ['&&', '||']:
            return True
        return False


class DeclarationNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        # TODO: duplicate name, comment temporarily
        # self.type = self.child_by_field_name('type')

        # a tricky solution since tree-sitter child_by_field_name
        # can only return the first field
        # for example, int a,b; returns a.
        self.decl_type = self.child_by_field_name('type')
        self.declarator = []
        for _c in self.children:
            if _c.type in [
                    'pointer_declarator', 'array_declarator', 'identifier',
                    'init_declarator'
            ]:
                self.declarator.append(_c)

    def declared_identifiers(self) -> List[IdentifierNode]:
        ids = []
        for _decl in self.declarator:
            unpack_type = [
                'pointer_declarator', 'array_declarator', 'init_declarator'
            ]
            while _decl.type in unpack_type:
                _decl = _decl.child_by_field_name('declarator')
            assert (_decl.type == 'identifier')
            ids.append(_decl)
        return ids


class ParenthesizedExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)

    def remove_parenthese(self):
        # children[0] and children[2] is ( and )
        return self.make_wrapper(self.internal.children[1])


class IfStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        from .abstract_node import IfConditionNode
        super().__init__(src, ts_node)
        self.condition = self.child_by_field_name('condition')
        # By AbstractNode, we assume there is a node with the type
        # if_condition, which is actually non-exist in tree-sitter.
        self.condition_abs = IfConditionNode(self.condition)
        self.consequence = self.child_by_field_name('consequence')
        self.alternative = self.child_by_field_name('alternative')

    def common_entry_constraints(self):
        return self.condition_abs.common_entry_constraints()

    def entry_constraints(self):
        return self.condition_abs.entry_constraints()


class FunctionDefinitionNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.type = self.child_by_field_name('type')
        self.body = self.child_by_field_name('body')
        function_declarator = self.child_by_field_name('declarator')
        while function_declarator.type == 'pointer_declarator':
            assert (isinstance(self.type, TypeNode))
            self.type.pointer_level += 1
            function_declarator = function_declarator.child_by_field_name(
                'declarator')
        self.name = function_declarator.child_by_field_name('declarator')
        parameter_list = function_declarator.child_by_field_name('parameters')
        self.parameters = parameter_list.children if parameter_list else list()
        # filter out bracket
        self.parameters = [
            _p for _p in self.parameters if _p.src not in ['(', ')']
        ]


class SubscriptExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.argument = self.child_by_field_name('argument')
        self.index = self.child_by_field_name('index')


class CallExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.function = self.child_by_field_name('function')
        self.arguments = self.child_by_field_name(
            'arguments').children  # at least ( and ) as children
        # filter out bracket
        self.arguments = [
            _a for _a in self.arguments if _a.src not in ['(', ')']
        ]

    def is_indirect(self) -> bool:
        """ whether the invocation is the indirect call
        """
        return not isinstance(self.function, IdentifierNode)


class ExpressionStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)


class AssignmentExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.left = self.child_by_field_name('left')
        self.right = self.child_by_field_name('right')


class InitDeclaratorNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.declarator = self.child_by_field_name('declarator')
        self.value = self.child_by_field_name('value')


class PreprocArgNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        # Tree-sitter parser will include the useless spaces
        # in preproc_arg, thus we do strip() for src.
        self.src = self.src.strip()


class PreprocDefNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.name = self.child_by_field_name('name')
        self.value = self.child_by_field_name('value')

    def __str__(self):
        return f'#define {self.name} {self.value}'

    def __repr__(self):
        return f'#define {self.name} {self.value}'


class EnumSpecifierNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.name = self.child_by_field_name('name')
        # inner property
        self._body: EnumeratorListNode = self.child_by_field_name('body')
        self.kv: dict = self._body.kv

    def unsolved_value(self):
        """
        helper function of conclude_value, outputs
        the symbols representing unknown values. One
        needs to provide the values of these symbols
        to perform conclude_value.
        """
        lst = []
        for _k, _v in self.kv.items():
            if _v and not isinstance(_v, NumberLiteralNode):
                lst.append(_v)
        return lst

    def conclude_value(self, value_dic=dict()) -> dict:
        """
        While self.kv provides the literal enum key and
        value, conclude_value tries to conclude the actual
        values that keys represent.

        For example, for the following enumeration:
            enum A {
                A1 = MACRO1, // #define MACRO1 1
                A2,
            };

        self.kv equals to {A1: MACRO1, A2: None}.

        However, with the value of MACRO1 provided by the
        parameter value_dic, conclude_value will output the
        dict like {A1: 1, A2: 2}.
        """

        def solve(val) -> Optional[int]:
            # the types of the values of the output dic are int and None
            if isinstance(val, NumberLiteralNode):
                return int(str(val))
            elif val in value_dic.keys():
                return int(value_dic[val])
            else:
                return None

        # 1. conclude the value of each item
        # 1.1 sort the items
        k_lst: List[BasicNode] = []
        for _k in self.kv.keys():
            if not k_lst:
                k_lst.append(_k)
                continue

            insert_idx = -1
            for _id, _ in enumerate(k_lst):
                if not _.in_front(_k):
                    insert_idx = _id
                    break
            # when _k is behind all elements in k_lst
            if insert_idx == -1:
                insert_idx = len(k_lst)
            k_lst.insert(insert_idx, _k)

        # 1.2 conclude the value
        dic: Dict[BasicNode, Optional[int]] = dict()
        for _id, _k in enumerate(k_lst):
            _v = self.kv[_k]
            if _id == 0 and _v is None:
                _v = 0
            elif _v is not None:
                _v = solve(_v)
            # query the previous element
            elif _v is None:
                pre_ele = dic[k_lst[_id - 1]]
                _v = pre_ele + 1 if type(pre_ele) == int else None
            else:
                assert (False)
            dic[_k] = _v
        return dic


class EnumeratorListNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.enumerator = self.children_by_type_name('enumerator')
        self.kv = dict()
        for _e in self.enumerator:
            self.kv[_e.name] = _e.value


class EnumeratorNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.name = self.child_by_field_name('name')
        self.value = self.child_by_field_name('value')


class ParameterDeclarationNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.type = self.child_by_field_name('type')
        self.declarator = self.child_by_field_name('declarator')
        # unpack the declarator to get the real name
        self.name = None
        # TODO: create more specific type node (use TypeNode as the super
        # class), since some types have additional properties, like
        # struct_specifier
        declarator = self.declarator
        # self.declarator maybe None, e.g. int func(void)
        while True and declarator:
            if declarator.type == 'pointer_declarator':
                declarator = declarator.child_by_field_name('declarator')
                self.type.pointer_level += 1
            elif declarator.type == 'array_declarator':
                declarator = declarator.child_by_field_name('declarator')
                self.type.array_level += 1
            elif declarator.type == 'identifier':
                self.name = declarator
                break
            else:
                assert (False)


class VariadicParameterNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)


class CompoundStatementNode(BasicNode):
    """ The wrapper of tree-sitter node 'compound_statement'.

    CompoundStatementNode is a collection of nodes. For
    example, it is used to represent the body of the function
    and loop node.

    Attributes:
        statements (list): the nodes contained in compound statement

    """

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.statements = self.children
