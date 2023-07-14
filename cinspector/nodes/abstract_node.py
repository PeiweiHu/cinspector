from .node import Node


class AbstractNode(Node):
    """
    AbstractNode is the base class of abstract node classes.
    The so-called abstract node is the node that exists for the convenience
    of analysis (for example, CFG generation). It doesn't correspond
    to the acutal code elemetnts.
    """

    def __init__(self, node_type=None) -> None:
        self.node_type = node_type


class BorderNode(AbstractNode):

    def __init__(self, node_type=None) -> None:
        super().__init__(node_type)

    def __str__(self) -> str:
        return self.node_type

    def __repr__(self) -> str:
        return self.node_type


class IfConditionNode(AbstractNode):

    def __init__(self, condition, node_type='if_condition') -> None:
        super().__init__(node_type)
        self.condition = condition
        self.start_point = self.condition.start_point
        self.end_point = self.condition.end_point

    def descendants_by_type_name(self, type_name):
        return self.condition.descendants_by_type_name(type_name)

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
        from .basic_node import ParenthesizedExpressionNode, BinaryExpressionNode
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

    def __init__(self, condition, node_type='y_if') -> None:
        super().__init__(condition, node_type)

    def __str__(self) -> str:
        return '[if][Y]' + str(self.condition)

    def __repr__(self) -> str:
        return '[if][Y]' + str(self.condition)


class NConditionNode(IfConditionNode):

    def __init__(self, condition, node_type='n_if') -> None:
        super().__init__(condition, node_type)

    def __str__(self) -> str:
        return '[if][N]' + str(self.condition)

    def __repr__(self) -> str:
        return '[if][N]' + str(self.condition)


class ForLoopNode(AbstractNode):

    def __init__(self,
                 initializer,
                 condition,
                 update,
                 node_type='loop_condition') -> None:
        self.node_type = node_type
        self.initializer = initializer
        self.condition = condition
        self.update = update

    def descendants_by_type_name(self, name):
        children = []
        if self.initializer:
            children += self.initializer.descendants_by_type_name(name)
        if self.condition:
            children += self.condition.descendants_by_type_name(name)
        if self.update:
            children += self.update.descendants_by_type_name(name)
        return children


class YForLoopNode(ForLoopNode):

    def __init__(self,
                 initializer,
                 condition,
                 update,
                 node_type='y_loop') -> None:
        super().__init__(initializer, condition, update, node_type)

    def __str__(self) -> str:
        return f'[for][Y]({self.initializer} {self.condition}; {self.update})'

    def __repr__(self) -> str:
        return f'[for][Y]({self.initializer} {self.condition}; {self.update})'


class NForLoopNode(ForLoopNode):

    def __init__(self,
                 initializer,
                 condition,
                 update,
                 node_type='n_loop') -> None:
        super().__init__(initializer, condition, update, node_type)

    def __str__(self) -> str:
        return f'[for][N]({self.initializer} {self.condition}; {self.update})'

    def __repr__(self) -> str:
        return f'[for][N]({self.initializer} {self.condition}; {self.update})'


class DoWhileLoopNode(AbstractNode):
    """
    Used to represent the condition of do-while loop
    """

    def __init__(self, condition, node_type='loop_condition') -> None:
        super().__init__(node_type)
        self.condition = condition

    def __str__(self) -> str:
        return f'[do-while][]({self.condition})'

    def __repr__(self) -> str:
        return f'[do-while][]({self.condition})'


class WhileLoopNode(AbstractNode):

    def __init__(self, condition, node_type='loop_condition') -> None:
        super().__init__(node_type)
        self.condition = condition

    def descendants_by_type_name(self, name):
        return self.condition.descendants_by_type_name(name)


class YWhileLoopNode(WhileLoopNode):

    def __init__(self, condition, node_type='y_loop') -> None:
        super().__init__(condition, node_type)

    def __str__(self) -> str:
        return f'[while][Y]({self.condition})'

    def __repr__(self) -> str:
        return f'[while][Y]({self.condition})'


class NWhileLoopNode(WhileLoopNode):

    def __init__(self, condition, node_type='n_loop') -> None:
        super().__init__(condition, node_type)

    def __str__(self) -> str:
        return f'[while][N]({self.condition})'

    def __repr__(self) -> str:
        return f'[while][N]({self.condition})'


class SwitchNode(AbstractNode):

    def __init__(self, condition, case_value, node_type='switch_node') -> None:
        super().__init__(node_type)
        self.condition = condition
        self.case_value = case_value

    def descendants_by_type_name(self, types):
        rtn = []
        if self.condition:
            rtn += self.condition.descendants_by_type_name(types)
        if self.case_value:
            rtn += self.case_value.descendants_by_type_name(types)
        return rtn

    def __str__(self) -> str:
        return f'switch {self.condition} case {self.case_value} '

    def __repr__(self) -> str:
        return f'switch {self.condition} case {self.case_value} '
