"""
Control Flow Graph-related analysis
"""
from networkx import DiGraph  # type: ignore
import networkx as nx  # type: ignore
from typing import Optional, Dict, Union, List
from cinspector.nodes import Util, BorderNode, Node
from cinspector.nodes import ForStatementNode, YForLoopNode, NForLoopNode
from cinspector.nodes import WhileStatementNode, YWhileLoopNode, NWhileLoopNode
from cinspector.nodes import IfStatementNode, YConditionNode, NConditionNode
from cinspector.nodes import SwitchNode, FunctionDefinitionNode
from cinspector.nodes import DoWhileLoopNode, DoStatementNode


class BasicBlock(Util):

    def __init__(self, nodes: list) -> None:
        self.nodes = nodes


class BaseCFG(Util):

    def __init__(self, stmts: List[Node]) -> None:
        self.stmts = stmts
        self.start: Optional[BorderNode] = None
        self.end: Optional[BorderNode] = None
        self.cfg = DiGraph()
        self.generate()

    def execution_path(self):
        path = list(nx.all_simple_paths(self.cfg, self.start, self.end))
        # filter out start and end
        path = [_[1:-1] for _ in path]
        return path

    def generate(self):
        """CFG.generate() generate the control flow graph"""
        """
        construct the initial state first
            int a, b;
            a = 1;
            b = 2;
        to:
             <START>
                |
            int a, b;
                |
            a = 1;
                |
            b = 2;
                |
              <END>
        """
        stmt_lst = self.stmts
        stmt_lst.insert(0, BorderNode(node_type='<START>'))
        stmt_lst.append(BorderNode(node_type='<END>'))
        self.start, self.end = stmt_lst[0], stmt_lst[-1]
        for _ in range(len(stmt_lst) - 1):
            self.cfg.add_edge(stmt_lst[_], stmt_lst[_ + 1])

        # iteratively detect branch
        cur = [self.start]
        """
        record the label and corresponding statement

        fail:
            free(sth);
            return -1;

        label_map will create the mapping between "fail" and free statement
        """
        label_map: Dict[str:Union[Node, List[Node]]] = dict()

        def _update_label_map(_c: Node, header: Union[Node, List[Node]]):
            """
            The initial recorded label statement may be
            deconstructed, we need to track this variation.
            The <header> may also be list, e.g. [ycond, ncond]
            for if statement. This function should typically
            invoked while some nodes is deleted in self.cfg.


            Args:
                _c (Node): the deleted node
                header (Union[Node, List[node]]): the statement that replaces _c

            Returns:
                no return value
            """
            update = list()
            for _k, _v in label_map.items():
                if _v == _c:
                    update.append(_k)
            for _u in update:
                # print(f'{_u}: {label_map[_u]} -> {header}')
                label_map[_u] = header

        while True:
            if not cur:
                break
            next = []
            changed = 0

            for _c in cur:
                next += list(self.cfg.successors(_c))

                if _c.node_type == 'compound_statement':
                    # divide compound statement directly
                    pred = list(self.cfg.predecessors(_c))
                    succ = list(self.cfg.successors(_c))
                    children = [
                        _ for _ in _c.children if not _.node_type in ['{', '}']
                    ]
                    # skip empty compound statement
                    if not children:
                        continue
                    # link every child
                    for _ in range(len(children) - 1):
                        self.cfg.add_edge(children[_], children[_ + 1])
                    # link the first and last child node with pred and succ node
                    for _p in pred:
                        self.cfg.add_edge(_p, children[0])
                    for _s in succ:
                        self.cfg.add_edge(children[-1], _s)
                    # remove the old node
                    self.cfg.remove_node(_c)
                    # since the graph is changed, analyse from scratch
                    changed = 1
                    _update_label_map(_c, children[0])

                elif _c.node_type == 'labeled_statement':
                    # record the statement corresponding to label
                    label = _c.child_by_field_name('label').src
                    label_statement = _c.children[-1]
                    label_map[label] = label_statement
                    # replace label with statement
                    pred = list(self.cfg.predecessors(_c))
                    succ = list(self.cfg.successors(_c))
                    for _p in pred:
                        self.cfg.add_edge(_p, label_statement)
                    for _s in succ:
                        self.cfg.add_edge(label_statement, _s)
                    # remove label node
                    self.cfg.remove_node(_c)
                    changed = 1
                    _update_label_map(_c, label_statement)

                elif _c.node_type == 'if_statement':
                    """
                    Ideally:
                    from:
                                pred
                                 |
                              condition
                            /           \
                        consequence     alternative
                            \           /
                                succ
                    to:
                                pred
                            /           \
                          ycond        ncond
                            |             |
                        consequence    alternative
                            \           /
                                succ

                    if alternative doesn't exist, the edge between alternative
                    and succ nodes will be replaced by the edge between ncond
                    and succ node.

                    from:
                                pred
                                 |
                              condition
                            /           \
                        consequence     |
                            \           /
                                succ
                    to:
                                pred
                            /           \
                          ycond          |
                           |             |
                        consequence    ncond
                            \           /
                                succ
                    """
                    assert (isinstance(_c, IfStatementNode))
                    ycond = YConditionNode(_c.condition)
                    ncond = NConditionNode(_c.condition)
                    self.cfg.add_edge(ycond, _c.consequence)
                    if _c.alternative:
                        self.cfg.add_edge(ncond, _c.alternative)
                    # add new edge. don't remove old edges, they will be removed while deleting old node
                    pred = list(self.cfg.predecessors(_c))
                    succ = list(self.cfg.successors(_c))
                    for _p in pred:
                        self.cfg.add_edge(_p, ycond)
                        self.cfg.add_edge(_p, ncond)
                    for _s in succ:
                        self.cfg.add_edge(_c.consequence, _s)
                        if _c.alternative:
                            self.cfg.add_edge(_c.alternative, _s)
                        else:
                            self.cfg.add_edge(ncond, _s)
                    # remove old node
                    self.cfg.remove_node(_c)
                    # since the graph is changed, analyse from scratch
                    changed = 1
                    _update_label_map(_c, [ycond, ncond])

                elif _c.node_type == 'switch_statement':
                    pred = list(self.cfg.predecessors(_c))
                    succ = list(self.cfg.successors(_c))
                    condition = _c.child_by_field_name('condition')
                    case_statement_lst = _c.descendants_by_type_name(
                        'case_statement')
                    _sw_node_lst = []
                    for _case_statement in case_statement_lst:
                        _value = _case_statement.child_by_field_name('value')
                        _sw_node = SwitchNode(condition, _value)
                        _sw_node_lst.append(_sw_node)
                        _children = []
                        for _ in _case_statement.children:
                            if _.node_type in ['case', ':', 'default']:
                                continue
                            if _value and _.src == _value.src:
                                continue
                            _children.append(_)
                        for _p in pred:
                            self.cfg.add_edge(_p, _sw_node)
                        # statements exist in case
                        if _children:
                            self.cfg.add_edge(_sw_node, _children[0])
                            for _ in range(len(_children) - 1):
                                self.cfg.add_edge(_children[_],
                                                  _children[_ + 1])
                            for _s in succ:
                                self.cfg.add_edge(_children[-1], _s)
                        # no statement within case
                        else:
                            for _s in succ:
                                self.cfg.add_edge(_sw_node, _s)
                    self.cfg.remove_node(_c)
                    changed = 1
                    _update_label_map(_c, _sw_node_lst)

                elif _c.node_type == 'return_statement':
                    """ To avoid the statements after return statement (e.g.
                        the labeled_statement) is ignored directly, we unlink
                        the return statement with successors later.
                    """
                    pass

                elif _c.node_type == 'for_statement':
                    assert (isinstance(_c, ForStatementNode))
                    yloop = YForLoopNode(_c.initializer, _c.condition,
                                         _c.update)
                    nloop = NForLoopNode(_c.initializer, _c.condition,
                                         _c.update)
                    if _c.body:
                        loop_body = _c.body
                        self.cfg.add_edge(yloop, loop_body)
                    else:
                        # loop body may not exist
                        loop_body = yloop
                    pred = list(self.cfg.predecessors(_c))
                    succ = list(self.cfg.successors(_c))
                    for _p in pred:
                        self.cfg.add_edge(_p, yloop)
                        self.cfg.add_edge(_p, nloop)
                    for _s in succ:
                        self.cfg.add_edge(loop_body, _s)
                        self.cfg.add_edge(nloop, _s)
                    # remove old for statement
                    self.cfg.remove_node(_c)
                    changed = 1
                    _update_label_map(_c, [yloop, nloop])

                elif _c.node_type == 'do_statement':
                    assert (isinstance(_c, DoStatementNode))
                    cond = DoWhileLoopNode(_c.condition)
                    body = _c.body
                    pred = list(self.cfg.predecessors(_c))
                    succ = list(self.cfg.successors(_c))
                    self.cfg.add_edge(body, cond)
                    for _p in pred:
                        self.cfg.add_edge(_p, body)
                    for _s in succ:
                        self.cfg.add_edge(cond, _s)
                    self.cfg.remove_node(_c)
                    changed = 1
                    _update_label_map(_c, [body])

                elif _c.node_type == 'while_statement':
                    assert (isinstance(_c, WhileStatementNode))
                    yloop = YWhileLoopNode(_c.condition)
                    nloop = NWhileLoopNode(_c.condition)
                    if _c.body:
                        loop_body = _c.body
                        self.cfg.add_edge(yloop, loop_body)
                    else:
                        # loop body may not exist
                        loop_body = yloop
                    pred = list(self.cfg.predecessors(_c))
                    succ = list(self.cfg.successors(_c))
                    for _p in pred:
                        self.cfg.add_edge(_p, yloop)
                        self.cfg.add_edge(_p, nloop)
                    for _s in succ:
                        self.cfg.add_edge(loop_body, _s)
                        self.cfg.add_edge(nloop, _s)
                    # remove old for statement
                    self.cfg.remove_node(_c)
                    changed = 1
                    _update_label_map(_c, [yloop, nloop])

                else:
                    assert "Undefined statement"

                if changed:
                    next = [self.start]
                    break

            # start analysing next nodes
            cur = next

        # link goto and label
        goto_lst = []
        for _n in self.cfg.nodes:
            if _n.node_type == 'goto_statement':
                goto_lst.append(_n)
                # remove old edges
                succ = list(self.cfg.successors(_n))
                for _s in succ:
                    self.cfg.remove_edge(_n, _s)

        for _g in goto_lst:
            label = _g.child_by_field_name('label').src
            assert (label in list(label_map.keys()))
            if not isinstance(label_map[label], list):
                label_map[label] = [label_map[label]]
            for _ in label_map[label]:
                self.cfg.add_edge(_g, _)

        # unlink return statement and successors
        for _n in self.cfg.nodes:
            if _n.node_type == 'return_statement':
                succ = list(self.cfg.successors(_n))
                for _s in succ:
                    self.cfg.remove_edge(_n, _s)
                self.cfg.add_edge(_n, self.end)

    def merge(self):
        """
        self.generate generate the DiGraph in which nodes are single statement
        self.merge merge the statements into the basic block
        """
        pass


class CFG(BaseCFG):

    def __init__(self, function_def: FunctionDefinitionNode) -> None:
        self.function_def = function_def
        stmt_lst = [
            _ for _ in self.function_def.body.children
            if _.node_type not in ['{', '}']
        ]
        super().__init__(stmt_lst)
