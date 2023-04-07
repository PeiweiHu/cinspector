""" Interfaces for users

This file defines several interfaces to ease the
use of cinspector.

In particular, CProj is the interface for the whole
C-based project, which usually contains some directories
including header and source files.

CCode is the base interface for any interfaces that
represent source code, such as CFile.
"""

import os
from collections import defaultdict
from typing import List, Any
from .nodes import BasicNode, FunctionDefinitionNode


class CProj:
    """ TODO
    """

    def __init__(self, proj_path: str) -> None:
        self.proj_path = proj_path


class CCode:

    def __init__(self, src) -> None:
        self.src = src
        self.node = BasicNode(self.src)
        # the following attributes maintain specific semantic elements
        self.func_lst: Any = None
        self.enum_lst: Any = None

    def get_by_type_name(self, type_name) -> list:
        return self.node.children_by_type_name(type_name)


class CFile(CCode):
    """ TODO
    """

    def __init__(self, file_path) -> None:
        self.file_path = file_path
