""" Interfaces for users

This file defines several interfaces to ease the
use of cinspector.

In particular, CProj is the interface for the whole
C-based project, which usually contains some directories
including header and source files.

CCode is the base interface for any interfaces that
represent source code, such as CFile.
"""

from typing import Dict, Callable
from .nodes import BasicNode, Node


class CProj:
    """ TODO
    """

    def __init__(self, proj_path: str) -> None:
        self.proj_path = proj_path


class CCode:

    def __init__(self, src) -> None:
        self.src = src
        self.node = BasicNode(self.src)

    def get_by_type_name(self, type_name: str) -> list:
        return self.node.descendants_by_type_name(type_name)

    def get_by_condition(self, condition: Callable[[Node], bool]) -> list:
        """
        Access the nodes that satisfy the condition
        """

        all_descendants = self.node.descendants()
        return [_ for _ in all_descendants if condition(_)]

    def get_by_type_name_and_query(self, type_name: str,
                                   query: Dict[str, str]) -> list:
        n_lst = self.get_by_type_name(type_name)
        return [n for n in n_lst if n.query(query)]

    def get_by_type_name_and_field(self, type_name: str,
                                   field: Dict[str, str]) -> list:
        """
        Access the nodes by assigning node_type and fields. Note that
        the nodes that don't statisfy the type requirements, don't own
        the assigned FIELDS, and don't own the assigned FIELD VALUES will
        be filter out.

        Return:
            list containing the nodes that satisfy the type and field
            requirements
        """

        n_lst = self.get_by_type_name(type_name)

        def own_field(n: BasicNode) -> bool:
            for _k, _v in field.items():
                child = n.child_by_field_name(_k)
                if not child:
                    return False
                if not _v == child.src:
                    return False
            return True

        return [n for n in n_lst if own_field(n)]


class CFile(CCode):
    """ TODO
    """

    def __init__(self, file_path) -> None:
        self.file_path = file_path
