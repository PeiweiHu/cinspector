"""
This file contains wrapper classes of tree-sitter nodes. In general,
the wrapper classes are designed following the following rules:

1. Naming Convention. The class is named based on the type of tree-sitter
node. For example, the wrapper class of tree-sitter node 'function_definition'
is named FunctionDefinitionNode.

2. Attributes. The attributes within each class can by divided into two
groups. The first group corresponds to the fields of tree-sitter node. For
example, the node of 'function_definition' type in tree-sitter has the
fields 'type', 'declarator', and 'body'. The wrapper class of
'function_definition' FunctionDefinitionNode will also contain the
attributes 'type', 'declarator', and 'body'. The second group of attributes
is added by cinspector to facilitate the analysis of source code. We call them
additional attributes.

3. Property representation. The properties of the node classes in this file,
i.e., classes inheriting from BasicNode, should be represented by BasicNode
instances as much as possible. For example, the property 'name' of the class
ParameterDeclarationNode is an instance of IdentifierNode instead of str. Of
course, the user can also get the str format by invoking the method src().
"""

from typing import List, Optional, Dict, Iterable, Union
from .node import Node, Util, Query


class BasicNode(Node, Util, Query):
    """ The ancestor of all wrapper classes of tree-sitter nodes

    For those tree-sitter nodes that do not have corresponding wrapper, they
    use BasicNode as the default wrapper.

    Pay attention to the difference betweeen <internal_src> and <src>.
    Considering the way cinspector is used, every BasicNode (or its subclass)
    belongs to a code snippet. The <internal_src> stores the source code of
    the whole code snippet while src stores the source code of the current
    node. For example, if we have a code snippet:

        int a;
        int func() {return 0;}

    Assume func_node represents the function <func> in the code snippet and is
    an instance of FunctionDefinitionNode. Then, the <src> of func_node is 'int
    func() {return 0;}'. While the <internal_src> of func_node is the whole
    code snippet.

    Attributes:
        internal_src (str): the source code of the whole code snippet.
        internal (tree_sitter.Node): the corresponding tree-sitter node of
            the current wrapper class.
        internal_tree (tree_sitter.Tree): the corresponding tree-sitter
            tree of the whole code snippet, internal belongs to this tree.
        node_type (str): the type of the current wrapper class.
        ts_type (str): deprecated, type of the corresponding tree-sitter node,
            we design this since the wrapper class and corresponding
            tree-sitter node may have different type under some situations.
        start_point (tuple): the start position of the current node in
            internal_src.
        end_point (tuple): the end position of the current node in
            internal_src.
        child_count (int): the number of children of the current node.
        src (str): the source code of the current node.

    Properties:
        parent (BasicNode): the parent node of the current node.
        children (List[BasicNode]): the children nodes of the current node.

    Methods:
        equal(_o: 'BasicNode'): check whether the current node is equal to _o.
        make_wrapper(ts_node: tree-sitter.Node): make a wrapper class for the
            tree-sitter node.
        child_by_field_name(field_name: str): get the specific field of the
            current node.
        descendants(): get all descendants.
        descendants_by_type_name(type_name: Union[str, List[str]): get the
            descendants nodes belonging to the specific type.
        print_tree(): print the parsed tree
    """

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        """
        Initialize the BasicNode

        Args:
            src (str): the source code of the WHOLE code snippet, not the
                current BasicNode.
            ts_node (tree_sitter.Node): the corresponding tree-sitter node of
                the current BasicNode
            ts_tree (tree_sitter.Tree): the corresponding tree-sitter tree of
                the WHOLE code snippet, this also is the tree that ts_node
                belongs to.

        Returns:
            None
        """

        self.internal_src = src
        """
        Ideally, the following condtion is true only when file content is
        passed to BasicNode. Other nodes such as FunctionDefinitionNode
        should be initialized with ts_node dictated.
        """
        if not ts_node:
            ts_tree = self.get_tree(src)
            ts_node = ts_tree.root_node
        self.internal = ts_node
        self.internal_tree = ts_tree
        self.node_type = ts_node.type
        # ts_type: deprecated, node_type should be totally consistent with the type of tree-sitter node
        self.ts_type = ts_node.type
        self._parent = None
        self.start_point = ts_node.start_point
        self.end_point = ts_node.end_point
        self.child_count = ts_node.child_count
        self._children = None
        self.src = self.internal.text.decode("utf8")

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
                # TODO: Maybe it's better to keep them for consistency.
                if _ch.type not in ['(', ')', ',', ';', '{', '}']
            ]
        return self._children

    def __str__(self) -> str:
        # return f'({self.type}){self.src}'
        return self.src

    def __repr__(self) -> str:
        # return f'({self.__hash__}){self.src}'
        return self.src

    def equal(self, _o: 'BasicNode') -> bool:
        assert (isinstance(_o, BasicNode))
        internal_src_eq = (self.internal_src == _o.internal_src)
        position_eq = (self.internal.start_point == _o.internal.start_point)
        position_eq = position_eq and (self.internal.end_point
                                       == _o.internal.end_point)
        return internal_src_eq and position_eq

    @property
    def parent(self):
        if not self._parent:
            self._parent = self.make_wrapper(self.internal.parent)
        return self._parent

    def in_front(self, node: 'BasicNode'):
        return self.start_point[0] < node.start_point[0] or \
            (self.start_point[0] == node.start_point[0] and self.start_point[1] < node.start_point[1])

    def make_wrapper(self, ts_node):
        if not ts_node:
            return None
        wrapper_dict = {
            'assignment_expression': AssignmentExpressionNode,
            'binary_expression': BinaryExpressionNode,
            'call_expression': CallExpressionNode,
            'cast_expression': CaseExpressionNode,
            'conditional_expression': ConditionalExpressionNode,
            'compound_statement': CompoundStatementNode,
            'declaration': DeclarationNode,
            'do_statement': DoStatementNode,
            'enum_specifier': EnumSpecifierNode,
            'enumerator_list': EnumeratorListNode,
            'enumerator': EnumeratorNode,
            'expression_statement': ExpressionStatementNode,
            'field_identifier': FieldIdentifierNode,
            'field_declaration_list': FieldDeclarationListNode,
            'field_declaration': FieldDeclarationNode,
            'function_definition': FunctionDefinitionNode,
            'function_declarator': FunctionDeclaratorNode,
            'for_statement': ForStatementNode,
            'if_statement': IfStatementNode,
            'init_declarator': InitDeclaratorNode,
            'identifier': IdentifierNode,
            'type_identifier': TypeIdentifierNode,
            'primitive_type': TypeNode,
            'number_literal': NumberLiteralNode,
            'parenthesized_expression': ParenthesizedExpressionNode,
            'preproc_function_def': PreprocFunctionDefNode,
            'preproc_def': PreprocDefNode,
            'preproc_arg': PreprocArgNode,
            'parameter_declaration': ParameterDeclarationNode,
            'parameter_list': ParameterListNode,
            'return_statement': ReturnStatementNode,
            'struct_specifier': StructSpecifierNode,
            'subscript_expression': SubscriptExpressionNode,
            'storage_class_specifier': StorageClassSpecifierNode,
            'sized_type_specifier': TypeNode,
            'macro_type_specifier': TypeNode,
            'type_qualifier': TypeQualifierNode,
            'type_identifier': TypeIdentifierNode,
            'unary_expression': UnaryExpressionNode,
            'variadic_parameter': VariadicParameterNode,
            'while_statement': WhileStatementNode,
        }
        init_func = wrapper_dict[
            ts_node.type] if ts_node.type in wrapper_dict.keys() else BasicNode
        return init_func(self.internal_src, ts_node, self.internal_tree)

    def child_by_field_name(self, name: str):
        assert (type(name) == str)
        return self.make_wrapper(self.internal.child_by_field_name(name))

    def descendants(self):
        """
        Depth-first traverse to collect all descendants of the
        current node, the current node itself will not be collected.
        """

        node_lst = []
        cursor = self.internal.walk()
        root_node = cursor.node
        while True:
            if cursor.node != root_node:
                node_lst.append(self.make_wrapper(cursor.node))
            if not cursor.goto_first_child():
                while not cursor.goto_next_sibling():
                    if not cursor.goto_parent():
                        return node_lst

    def descendants_by_type_name(self, name: Union[str, List[str]]):
        """
        Depth-first traverse to collect all descendants that satisfy the node_type
        requirements.
        """

        if type(name) == str:
            name = [name]

        return [_ for _ in self.descendants() if _.node_type in name]

    def tokenize(self) -> List['BasicNode']:
        """Tokenize the current code snippet

        Returns:
            A list (order-sensitive) of tokens

        """

        level = 0
        node_lst = []
        cursor = self.internal.walk()
        while True:
            # only append leaf nodes
            if not cursor.node.children:
                node_lst.append(self.make_wrapper(cursor.node))

            if not cursor.goto_first_child():
                while not cursor.goto_next_sibling():
                    if not cursor.goto_parent():
                        return node_lst
                    else:
                        level -= 1
            else:
                level += 1

    def print_tree(self):
        """
        Print the parsed tree
        """

        def _tree_nodes():
            level = 0
            node_lst = []
            cursor = self.internal.walk()
            while True:
                node_lst.append((self.make_wrapper(cursor.node), level))
                if not cursor.goto_first_child():
                    while not cursor.goto_next_sibling():
                        if not cursor.goto_parent():
                            return node_lst
                        else:
                            level -= 1
                else:
                    level += 1

        nlst = _tree_nodes()
        for _n in nlst:
            node, level = _n
            # prepare the format
            indent = " " * 4 * level
            t = f"type={node.node_type}"
            pos = f"start_point={node.start_point} end_point={node.end_point}"
            print(indent, type(node).__name__, t, pos, node.src.__repr__())


# currently only add commonly used type
class TypeNode(BasicNode):
    """
    TODO: remove the pointer_level and array_level, use analysis
    module to conclude the related property.
    """

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.pointer_level = 0
        self.array_level = 0

    def is_pointer(self):
        return self.pointer_level != 0

    def is_array(self):
        return self.array_level != 0


class TypeIdentifierNode(BasicNode):
    """ Wrapper for type_identifier node in tree-sitter
    """
    pass


class FieldIdentifierNode(BasicNode):
    """ Wrapper for field_identifier node in tree-sitter
    """
    pass


class FieldDeclarationListNode(BasicNode):
    """ Wrapper for field_declaration_list node in tree-sitter

    One can get all field_declaration by children()
    """
    pass


class FieldDeclarationNode(BasicNode):
    """ Wrapper for field_declaration node in tree-sitter
    """

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.type: BasicNode = self.child_by_field_name('type')
        # declarator is None for the field declaration of anonymous struct
        self.declarator: Optional[BasicNode] = self.child_by_field_name(
            'declarator')


class StructSpecifierNode(BasicNode):
    """ Wrapper for struct_specifier node in Tree-sitter
    """

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        # name may be None for anaonymous struct
        self.name: Optional[TypeIdentifierNode] = self.child_by_field_name(
            'name')
        self.body: FieldDeclarationListNode = self.child_by_field_name('body')

    def _type_identifier_result(self) -> Optional[str]:
        return self.name.src if self.name else None


class TypeQualifierNode(BasicNode):
    """ Wrapper for type qualifier node in tree-sitter

    A type qualifier is a keyword that is applied to a type,
    resulting in a qualified type.

    As of 2014 and C11, there are four type qualifiers in
    standard C: const (C89), volatile (C89), restrict (C99)
    and _Atomic (C11)
    """
    pass


class StorageClassSpecifierNode(BasicNode):
    """ Wrapper for storage class specifier node in tree-sitter

    Every variable has two properties in C language that are: data
    type (int, char, float, etc.) and storage class. The Storage
    Class of a variable decides its scope, lifetime, storage location,
    and default value.

    There are four storage classes in C language: auto, extern,
    static, and register.
    """

    pass


class WhileStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.condition = self.child_by_field_name('condition')
        if self.children:
            self.body = self.children[-1]
        else:
            self.body = None


class IdentifierNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)

    def __eq__(self, obj):
        return super().__eq__(obj)

    def __hash__(self):
        return super().__hash__()


class CaseExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.type = self.child_by_field_name('type')
        self.value = self.child_by_field_name('value')


class UnaryExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.argument = self.child_by_field_name('argument')

    def used_ids(self):
        ids = self.descendants_by_type_name('identifier')
        return ids


class ConditionalExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.condition = self.child_by_field_name('condition')
        self.consequence = self.child_by_field_name('consequence')
        self.alternative = self.child_by_field_name('alternative')


class NumberLiteralNode(BasicNode):

    pass


class ReturnStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.value = self.children[1] if len(self.children) > 1 else None


class PreprocFunctionDefNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.name = self.child_by_field_name('name')
        self.parameters = self.child_by_field_name('parameters')
        self.value = self.child_by_field_name('value')


class ForStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.initializer = self.child_by_field_name('initializer')
        self.condition = self.child_by_field_name('condition')
        self.update = self.child_by_field_name('update')
        if self.children:
            self.body = self.children[-1]
        else:
            self.body = None


class BinaryExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.left = self.child_by_field_name('left')
        self.right = self.child_by_field_name('right')
        self.symbol = self.get_raw(self.internal_src, self.left.end_point,
                                   self.right.start_point)
        if self.symbol:
            self.symbol = self.symbol.strip()

    def is_logic_op(self):
        if self.symbol in ['&&', '||']:
            return True
        return False


class DeclarationNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        # TODO: duplicate name, comment temporarily
        # self.type = self.child_by_field_name('type')

        # a tricky solution since tree-sitter child_by_field_name
        # can only return the first field
        # for example, int a,b; returns a.
        self.type = self.child_by_field_name('type')
        self.declarator = []
        for _c in self.children:
            if _c.node_type in [
                    'pointer_declarator',
                    'array_declarator',
                    'identifier',
                    'init_declarator',
                    'function_declarator',
            ]:
                self.declarator.append(_c)

    def declared_identifiers(self) -> List[IdentifierNode]:
        ids = []
        for _decl in self.declarator:
            unpack_type = [
                'pointer_declarator',
                'array_declarator',
                'init_declarator',
                'function_declarator',
            ]
            while _decl.node_type in unpack_type:
                _decl = _decl.child_by_field_name('declarator')
            assert (_decl.node_type == 'identifier')
            ids.append(_decl)
        return ids


class DoStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.body = self.child_by_field_name('body')
        self.condition = self.child_by_field_name('condition')


class ParenthesizedExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)

    def remove_parenthese(self):
        # children[0] and children[2] is ( and )
        return self.make_wrapper(self.internal.children[1])


class IfStatementNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        from .abstract_node import IfConditionNode
        super().__init__(src, ts_node, ts_tree)
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


class ParameterDeclarationNode(BasicNode):
    """ The wrapper of the parameter_declaration node in tree-sitter.

    Attributes:
        type (TypeNode): the type of the parameter.
        declarator (Optional[BasicNode]): the declarator of the parameter,
            this can be None, e.g. int func(void), or the declaration
            int func(int).
    """

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)

        # fields of the tree-sitter node
        self.type = self.child_by_field_name('type')
        self.declarator = self.child_by_field_name('declarator')

    @property
    def type_qualifier(self) -> List[TypeQualifierNode]:
        """
        get the type qualifier of the parameter
        """

        return [_c for _c in self.children if isinstance(_c, TypeQualifierNode)]

    @property
    def storage_class_specifier(self) -> List[StorageClassSpecifierNode]:
        """
        get the storage class specifier of the parameter
        """

        return [
            _c for _c in self.children
            if isinstance(_c, StorageClassSpecifierNode)
        ]

    @property
    def name(self) -> Optional[IdentifierNode]:
        """
        try to analyse the name of the parameter
        """
        declarator = self.declarator
        # self.declarator maybe None, e.g. int func(void)
        while True and declarator:
            # int func(int *a)
            if declarator.node_type == 'pointer_declarator':
                declarator = declarator.child_by_field_name('declarator')
            # mainly in declaration such as int func(int *)
            elif declarator.node_type == 'abstract_pointer_declarator':
                return None
            # int func(int (*a)())
            elif declarator.node_type == 'function_declarator':
                declarator = declarator.child_by_field_name('declarator')
            # int func(int (*a)())
            elif declarator.node_type == 'parenthesized_declarator':
                declarator = declarator.children[0]
            # int func(int a[])
            elif declarator.node_type == 'array_declarator':
                declarator = declarator.child_by_field_name('declarator')
            # int func(int a)
            elif declarator.node_type == 'identifier':
                return declarator
            else:
                assert (False)
        return None


class ParameterListNode(BasicNode):
    """ The wrapper of the parameter_list node in tree-sitter.

    ParameterListNode is a collection of ParameterDeclarationNode.
    You can visit the children of ParameterListNode by the attributes
    <children>.
    """

    pass


class FunctionDeclaratorNode(BasicNode):
    """ wrapper of the function_declarator node in tree-sitter

    Attributes:
        declarator (BasicNode): declarator
        parameters (ParameterListNode): parameters
    """

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.declarator: BasicNode = self.child_by_field_name('declarator')
        self.parameters: ParameterListNode = self.child_by_field_name(
            'parameters')


class FunctionDefinitionNode(BasicNode):
    """Wrapper class of the function_definition node in tree-sitter

    Attributes:
        type (TypeNode): the type of the function
        declarator (FunctionDeclaratorNode): the declarator of the function
        body (CompoundStatementNode): the body of the function

    TODO: name may be None under some cases
    """

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.type: TypeNode = self.child_by_field_name('type')
        self.declarator: FunctionDeclaratorNode = self.child_by_field_name(
            'declarator')
        self.body: CompoundStatementNode = self.child_by_field_name('body')

    def _identifier_result(self) -> Optional[str]:
        return self.name.src

    def __get_nest_function_declarator(self) -> FunctionDeclaratorNode:
        """
        function_declarator may be nested, e.g. int (*func(int a))(int b).
        This function find the innermost one, i.e., func(int a).
        """
        declarator = self.declarator
        last_function_declarator = declarator
        # try to find out the nest function_declarator
        while True:
            if declarator.node_type == 'function_declarator':
                last_function_declarator = declarator
                declarator = declarator.child_by_field_name('declarator')
            elif declarator.node_type == 'parenthesized_declarator':
                declarator = declarator.children[0]
            elif declarator.node_type == 'pointer_declarator':
                declarator = declarator.child_by_field_name('declarator')
            elif declarator.node_type == 'identifier':
                break
            else:
                assert (0)
        return last_function_declarator

    @property
    def name(self) -> IdentifierNode:
        """
        conclude the name of the function
        """

        return self.__get_nest_function_declarator().child_by_field_name(
            'declarator')

    @property
    def parameters(self) -> ParameterListNode:
        """ conclude the parameters of the function

        The node function_declarator in tree-sitter has two fields:
        declarator and parameters. However, the field parameters is
        not strictly the real parameters of the current function.
        For example, for the function `int (*bar(int a))(int)`, the
        field parameters of the function_declarator `(*bar(int a))(int)`
        is `(int)`, while `int a` is the real parameter of the function.
        """

        return self.__get_nest_function_declarator().child_by_field_name(
            'parameters')

    @property
    def type_qualifier(self) -> List[TypeQualifierNode]:
        """
        get the type qualifier of the parameter
        """

        return [_c for _c in self.children if isinstance(_c, TypeQualifierNode)]

    @property
    def storage_class_specifier(self) -> List[StorageClassSpecifierNode]:
        """
        get the storage class specifier of the parameter
        """

        return [
            _c for _c in self.children
            if isinstance(_c, StorageClassSpecifierNode)
        ]

    @property
    def static(self) -> bool:
        """
        Whether the function is static
        """
        storage_class_specifiers = [_.src for _ in self.children]
        return True if 'static' in storage_class_specifiers else False

    @property
    def inline(self) -> bool:
        """
        Whether the function is inline
        """
        storage_class_specifiers = [_.src for _ in self.children]
        return True if 'inline' in storage_class_specifiers else False


class SubscriptExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.argument = self.child_by_field_name('argument')
        self.index = self.child_by_field_name('index')


class CallExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
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

    pass


class AssignmentExpressionNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.left = self.child_by_field_name('left')
        self.right = self.child_by_field_name('right')

    @property
    def symbol(self) -> str:
        """
        Return the symbol of the assignment expression, e.g.,
        a |= b owns the symbol |=.
        """

        symbol_start = self.left.internal.end_byte
        symbol_end = self.right.internal.start_byte
        return self.internal_src[symbol_start + 1:symbol_end].strip()


class InitDeclaratorNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.declarator = self.child_by_field_name('declarator')
        self.value = self.child_by_field_name('value')


class PreprocArgNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        # Tree-sitter parser will include the useless spaces
        # in preproc_arg, thus we do strip() for src.
        self.src = self.src.strip()


class PreprocDefNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.name = self.child_by_field_name('name')
        self.value = self.child_by_field_name('value')

    def __str__(self):
        return f'#define {self.name} {self.value}'

    def __repr__(self):
        return f'#define {self.name} {self.value}'


class EnumSpecifierNode(BasicNode):
    """
    wrapper of the tree-sitter node with the type <enum_specifier>

    Note that EnumSpecifierNode has different formats:

    1. enum Hash { A, B};  -> the whole string except ';' is EnumSpecifierNode
    2. void func(enum Hash h);  -> <enum Hash> is EnumSpecifierNode, currently
        this node has no filed <body>

    """

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.name: Optional[TypeIdentifierNode] = self.child_by_field_name(
            'name')
        # inner property
        self._body: EnumeratorListNode = self.child_by_field_name('body')
        self.kv: dict = self._body.kv if self._body else dict()

    def _type_identifier_result(self) -> Optional[str]:
        return self.name.src if self.name else None

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

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.enumerator = self.descendants_by_type_name('enumerator')
        self.kv = dict()
        for _e in self.enumerator:
            self.kv[_e.name] = _e.value


class EnumeratorNode(BasicNode):

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.name = self.child_by_field_name('name')
        self.value = self.child_by_field_name('value')


class VariadicParameterNode(BasicNode):

    pass


class CompoundStatementNode(BasicNode):
    """ The wrapper of tree-sitter node 'compound_statement'.

    CompoundStatementNode is a collection of nodes. For
    example, it is used to represent the body of the function
    and loop node.

    Attributes:
        statements (list): the nodes contained in compound statement

    """

    def __init__(self, src: str, ts_node=None, ts_tree=None) -> None:
        super().__init__(src, ts_node, ts_tree)
        self.statements = self.children
