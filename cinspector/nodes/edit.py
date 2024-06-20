"""
Edit nodes
"""

from __future__ import annotations
from typing import Tuple, List, Optional
from .basic_node import BasicNode
from .node import Util


class EditPos:

    def __init__(self, start: int, end: int, new_snippet: str) -> None:
        self.start = start
        self.end = end
        self.new_snippet = new_snippet


def edit_str(s: str, edits: List[EditPos]) -> Optional[str]:

    edits = sorted(edits, key=lambda x: x.start)

    for i in range(len(edits)):

        # check whether there is overlap in the edits
        if i != len(edits) - 1 and edits[i].end > edits[i + 1].start:
            return None

        # check whether the start and end are within the string
        if edits[i].start < 0 or edits[i].end > len(s):
            return None

    # start replacing
    s_lst = list(s)
    gap_cnt = 0
    for edit in edits:
        s_lst[edit.start + gap_cnt:edit.end + gap_cnt] = list(edit.new_snippet)
        gap = len(edit.new_snippet) - (edit.end - edit.start)
        gap_cnt += gap

    return ''.join(s_lst)


class Edit(Util):
    """ Edit the BasicNode

    This class is designed for editing the BasicNode,
    including adding, deleting, and replacing the children.

    """

    def __init__(self, target: BasicNode):
        self.target: BasicNode = target

    def is_child(self, child: BasicNode) -> bool:
        """
        whether the child node is the child of self.target,
        check by 1. same tree_sitter.Tree 2. start and end point
        """

        if self.target.internal_tree != child.internal_tree:
            return False

        # we don't treat the node itself as its child
        if self.target.start_point == child.start_point \
                and self.target.end_point == child.end_point:
            return False

        def is_infront(a1: Tuple[int, int], a2: Tuple[int, int]) -> bool:
            """
            whether a1 is infront of a2, leverage the default
            tuple comparison
            """

            return a1 <= a2

        return is_infront(self.target.start_point, child.start_point) \
            and is_infront(child.end_point, self.target.end_point)

    def _remove_child_src(self, child: BasicNode) -> str:
        """
        remove child's source code from self.target.internal_src

        Returns:
            the new source code
        """

        internal_src = self.target.internal_src
        start_byte = child.internal.start_byte
        end_byte = child.internal.end_byte
        return internal_src[:start_byte] + internal_src[end_byte:]

    def remove_child(self, child: BasicNode):
        """ Remove the child from the target node

        Args:
            child: the child to be removed
        """

        # check whether child's position is legal
        assert (self.is_child(child))

        # remove the child from the children list
        new_src = self._remove_child_src(child)
        tree = self.target.internal_tree
        tree.edit(
            start_byte=child.internal.start_byte,
            old_end_byte=child.internal.end_byte,
            new_end_byte=child.internal.start_byte,
            start_point=child.internal.start_point,
            old_end_point=child.internal.end_point,
            new_end_point=child.internal.start_point,
        )
        parser = self.get_parser()
        new_tree = parser.parse(bytes(new_src, 'utf8'), tree)
        """
        relocate to the target node, since we delete the child
        of self.target, the start_point of self.target should
        be unchanged.
        """
        old_start_point = self.target.start_point
        node_type = self.target.node_type
        # construct the BasicNode
        bn = BasicNode(new_src, new_tree.root_node, new_tree)
        target = None
        for _ in bn.descendants_by_type_name(node_type):
            if _.start_point == old_start_point:
                target = _
                break
        assert (target is not None)
        return target
