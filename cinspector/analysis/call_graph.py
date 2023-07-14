"""
Call Graph
"""

from typing import Iterable
from networkx import DiGraph  # type: ignore
from cinspector.nodes import FunctionDefinitionNode, CallExpressionNode, VariadicParameterNode


class CallGraph:
    """ Generate the call graph

    Accept a list of function nodes and analyze the
    invocation relationship between them. Note that
    only explicit invocations will be catched instead
    of indirect calls.

    Attribtes:
        funcs (Iterable[FunctionDefinitionNode]): involved functions
    """

    def __init__(self, funcs: Iterable[FunctionDefinitionNode]) -> None:
        self.funcs = funcs

    def is_identical(self, call: CallExpressionNode,
                     func: FunctionDefinitionNode) -> bool:
        """ check whether the <call> is the invocation of <func>

        We involve two checks to decide whether <call> is the invocation of <func>
            1. same func name
            2. same parameter number

        #TODO: It would be more precise if add parameter type check. But this
        requires dataflow analysis which we will implement later.
        """

        assert (not call.is_indirect())
        # name check
        call_name = call.function.src
        func_name = func.name.src
        name_check = call_name == func_name

        # parameter check
        call_para_num = len(call.arguments)
        fixed_para_num = 0
        variadic_para = False
        for _a in func.parameters.children:
            if isinstance(_a, VariadicParameterNode):
                variadic_para = True
            else:
                fixed_para_num += 1
        if variadic_para:
            para_num_check = call_para_num >= fixed_para_num
        else:
            para_num_check = call_para_num == fixed_para_num
        return name_check and para_num_check

    def analysis(self) -> DiGraph:
        graph = DiGraph()
        for _f in self.funcs:
            graph.add_node(_f)
            # start analyzing each function
            calls = _f.descendants_by_type_name('call_expression')
            for _c in calls:
                if _c.is_indirect():
                    continue
                for _ in self.funcs:
                    if self.is_identical(_c, _):
                        graph.add_edge(_f, _)
        return graph
