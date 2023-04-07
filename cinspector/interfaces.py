""" Interfaces for users

This file defines several interfaces to ease the
use of cinspector.

In particular, CProj is the interface for the whole
C-based project, which usually contains some directories
including header and source files.

CCode is the base interface for any interfaces that
represent source code, such as CFile.
"""

from typing import Dict
from .nodes import BasicNode


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
        return self.node.children_by_type_name(type_name)

    def get_by_type_name_and_query(self, type_name: str,
                                   query: Dict[str, str]) -> list:
        n_lst = self.get_by_type_name(type_name)
        return [n for n in n_lst if n.query(query)]


class CFile(CCode):
    """ TODO
    """

    def __init__(self, file_path) -> None:
        self.file_path = file_path
