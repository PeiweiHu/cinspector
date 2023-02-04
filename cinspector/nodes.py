"""
Make a wrapper of tree-sitter node
"""
import os
from tree_sitter import Language, Parser


class Util():

    def get_parser(self):
        abs_path = os.path.abspath(__file__)
        dire = os.path.dirname(abs_path)
        C_LANGUAGE = Language(f'{dire}/tree-sitter.so', 'c')
        parser = Parser()
        parser.set_language(C_LANGUAGE)
        return parser

    def get_tree(self, src: str):
        parser = self.get_parser()
        tree = parser.parse(bytes(src, 'utf8'))
        return tree

    def get_cursor(self, src: str):
        parser = self.get_parser()
        tree = parser.parse(bytes(src, 'utf8'))
        return tree.walk()

    def get_raw(self, s: str, start: tuple, end: tuple):
        lst = s.split('\n')
        s_row, s_col = start
        e_row, e_col = end

        if s_row > e_row or (s_row == e_row and s_col >= e_col):
            return None

        # potential bug: corresponding line does not have enough character
        if s_row == e_row:
            return lst[s_row][s_col:e_col]
        elif s_row + 1 == e_row:
            return lst[s_row][s_col:] + '\n' + lst[e_row][:e_col]
        else:
            return lst[s_row][s_col:] \
                    + '\n'.join(lst[s_row+1:e_row]) \
                    + lst[e_row][:e_col]

    def get_node_raw(self, s: str, node):
        if not node:
            return None
        return self.get_raw(s, node.start_point, node.end_point)


class AbstractNode():
    """
    AbstractNode is the base class of abstract node classes.
    The so-called abstract node is the node that exists for the convenience
    of analysis. It doesn't correspond to the acutal code elemetnts.
    """

    def __init__(self, type=None) -> None:
        self.type = type


class BorderNode(AbstractNode):

    def __init__(self, type=None) -> None:
        super().__init__(type)

    def __str__(self) -> str:
        return self.type

    def __repr__(self) -> str:
        return self.type


class IfConditionNode(AbstractNode):

    def __init__(self, condition, type='if_condition') -> None:
        super().__init__(type)
        self.condition = condition
        self.start_point = self.condition.start_point
        self.end_point = self.condition.end_point

    def children_by_type_name(self, type_name):
        return self.condition.children_by_type_name(type_name)

    def common_entry_constraints(self):
        """
        Many possible entry constraints exist for one condition.
        There are some strong constraints that are contained in every
        entry constraint.

        For example, for condition if (a < 1 && (b < 0 || b > 1)),
        it contains entry constraints [[a < 1, b < 0], [a < 1, b > 1]],
        a < 1 is a strong constraint. In other word, it is a must
        obeyed constraint.

        This function also a one-dimension list.
        """
        common_constraints = []
        e_cons = self.entry_constraints()
        # the comparison can be conducted by BasicNode.src or BasicNode.equal()
        for _e in e_cons[0]:  # checking the first is enough
            yes = True
            for _cons in e_cons[1:]:
                _cons_src = [_.src for _ in _cons]
                if _e.src not in _cons_src:
                    yes = False
            if yes:
                common_constraints.append(_e)
        return common_constraints

    def entry_constraints(self):
        """
        output the constraints for going into the condition
        it returns a two-dimension list

        if (a || (a < 1 && a > 0)) -> (a) (a < 1, a > 0)
        if (b && (a < 1 || a > 0)) -> (b, a < 1) (b, a > 0)
        """
        return self._constraints(self.condition)

    def _constraints(self, node):
        # proud of elegant code :-)
        if isinstance(node, ParenthesizedExpressionNode):
            assert (len(node.children) == 1)
            node = node.children[0]

        if isinstance(node, BinaryExpressionNode):
            if node.symbol == '||':
                return self._constraints(node.left) + self._constraints(
                    node.right)
            if node.symbol == '&&':
                """
                [[a,b], [c,d]] && [[e,f]] -> [[a,b,e,f], [c,d,e,f]]
                """
                ret = []
                _right_constraints = self._constraints(node.right)
                for _left in self._constraints(node.left):
                    for _right in _right_constraints:
                        ret.append(_left + _right)
                return ret
            if node.symbol in ['>', '<', '>=', '<=', '==']:
                return [[node]]

        return [[node]]


class YConditionNode(IfConditionNode):

    def __init__(self, condition, type='y_if') -> None:
        super().__init__(condition, type)

    def __str__(self) -> str:
        return '(Y)' + str(self.condition)

    def __repr__(self) -> str:
        return '(Y)' + str(self.condition)


class NConditionNode(IfConditionNode):

    def __init__(self, condition, type='n_if') -> None:
        super().__init__(condition, type)

    def __str__(self) -> str:
        return '(N)' + str(self.condition)

    def __repr__(self) -> str:
        return '(N)' + str(self.condition)


class ForLoopNode(AbstractNode):

    def __init__(self,
                 initializer,
                 condition,
                 update,
                 type='loop_condition') -> None:
        self.type = type
        self.initializer = initializer
        self.condition = condition
        self.update = update

    def children_by_type_name(self, name):
        children = []
        if self.initializer:
            children += self.initializer.children_by_type_name(name)
        if self.condition:
            children += self.condition.children_by_type_name(name)
        if self.update:
            children += self.update.children_by_type_name(name)
        return children


class YForLoopNode(ForLoopNode):

    def __init__(self, initializer, condition, update, type='y_loop') -> None:
        super().__init__(initializer, condition, update, type)

    def __str__(self) -> str:
        return f'Y({self.initializer} {self.condition}; {self.update})'

    def __repr__(self) -> str:
        return f'Y({self.initializer} {self.condition}; {self.update})'


class NForLoopNode(ForLoopNode):

    def __init__(self, initializer, condition, update, type='n_loop') -> None:
        super().__init__(initializer, condition, update, type)

    def __str__(self) -> str:
        return f'N({self.initializer} {self.condition}; {self.update})'

    def __repr__(self) -> str:
        return f'N({self.initializer} {self.condition}; {self.update})'


class WhileLoopNode(AbstractNode):

    def __init__(self, condition, type='loop_condition') -> None:
        super().__init__(type)
        self.condition = condition

    def children_by_type_name(self, name):
        return self.condition.children_by_type_name(name)


class YWhileLoopNode(WhileLoopNode):

    def __init__(self, condition, type='y_loop') -> None:
        super().__init__(condition, type)

    def __str__(self) -> str:
        return f'Y({self.condition})'

    def __repr__(self) -> str:
        return f'Y({self.condition})'


class NWhileLoopNode(WhileLoopNode):

    def __init__(self, condition, type='n_loop') -> None:
        super().__init__(condition, type)

    def __str__(self) -> str:
        return f'N({self.condition})'

    def __repr__(self) -> str:
        return f'N({self.condition})'


class SwitchNode(AbstractNode):

    def __init__(self, condition, case_value, type='switch_node') -> None:
        super().__init__(type)
        self.condition = condition
        self.case_value = case_value

    def children_by_type_name(self, types):
        rtn = []
        if self.condition:
            rtn += self.condition.children_by_type_name(types)
        if self.case_value:
            rtn += self.case_value.children_by_type_name(types)
        return rtn

    def __str__(self) -> str:
        return f'switch {self.condition} case {self.case_value} '

    def __repr__(self) -> str:
        return f'switch {self.condition} case {self.case_value} '


class BasicNode(Util):

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

    def equal(self, __o: object) -> bool:
        is_node = isinstance(__o, BasicNode)
        internal_src_eq = (self.internal_src == __o.internal_src)
        position_eq = (self.ts_node.start_point == __o.ts_node.start_point)
        position_eq = position_eq and (self.ts_node.end_point
                                       == __o.ts_node.end_point)
        return is_node and internal_src_eq and position_eq

    @property
    def parent(self):
        if not self._parent:
            self._parent = self.make_wrapper(self.internal.parent)
        return self._parent

    def in_front(self, node):
        return self.start_point[0] < node.start_point[0] or \
            (self.start_point[0] == node.start_point[0] and self.start_point[1] < node.start_point[1])

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
            'enum_specifier': EnumSpecifierNode,
            'enumerator_list': EnumeratorListNode,
            'enumerator': EnumeratorNode,
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

    def is_pointer(self):
        return self.pointer_level != 0


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
        self.declarator = []
        for _c in self.children:
            if _c.type in [
                    'pointer_declarator', 'array_declarator', 'identifier',
                    'init_declarator'
            ]:
                self.declarator.append(_c)


class ParenthesizedExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)


class IfStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None) -> None:
        super().__init__(src, ts_node)
        self.condition = self.child_by_field_name('condition')
        self.consequence = self.child_by_field_name('consequence')
        self.alternative = self.child_by_field_name('alternative')


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
        self._body = self.child_by_field_name('body')
        self.kv = self._body.kv

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

        def solve(val):
            # the types of the values of the output dic are int and None
            if isinstance(val, NumberLiteralNode):
                return int(str(val))
            elif val in value_dic.keys():
                return int(value_dic[val])
            else:
                return None

        # 1. conclude the value of each item
        # 1.1 sort the items
        k_lst = []
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
        dic = dict()
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
                assert(False)
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
