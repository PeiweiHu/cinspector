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

    def __init__(self, proj_path: str) -> None:
        self.proj_path = proj_path
        self.funcs: List[FunctionDefinitionNode] = []

    def count_file(self, ext):
        if type(ext) == str:
            ext = [ext]

        assert (os.path.exists(self.proj_path))
        res = defaultdict(int)
        for _r, _d, _fs in os.walk(self.proj_path):
            for _f in _fs:
                for _e in ext:
                    if _f.endswith('.' + _e):
                        res[_e] += 1
        return res

    def get_file(self, ext=['.c', '.h']) -> list:
        if type(ext) == str:
            ext = [ext]

        assert (os.path.exists(self.proj_path))
        res = []
        for _r, _d, _fs in os.walk(self.proj_path):
            for _f in _fs:
                for _e in ext:
                    _e = '.' + _e.lstrip('.')
                    if _f.endswith(_e):
                        res.append(os.path.join(_r, _f))
        return res

    def get_func(self, ext=['.c', '.h']) -> list:
        if type(ext) == str:
            ext = [ext]

        self.funcs = []
        fs = self.get_file(ext=ext)
        for _f in fs:
            try:
                cf = CFile(file_path=_f)
                self.funcs += cf.get_all_func()
            except Exception as e:
                continue
        return self.funcs

    def find_func(self, func_name):
        if not self.funcs:
            self.get_all_func()

        rtn = []  # may contain functions with the same name
        for _f in self.funcs:
            if _f.name and _f.name.src == func_name.strip():
                rtn.append(_f)
        return rtn


class CCode:

    def __init__(self, src) -> None:
        self.src = src
        self.node = BasicNode(self.src)
        # the following attributes maintain specific semantic elements
        self.func_lst: Any = None
        self.enum_lst: Any = None

    def get_by_type_name(self, type_name) -> list:
        return self.node.children_by_type_name(type_name)

    def get_all_func(self) -> list:
        if self.func_lst is None:
            self.func_lst = self.get_by_type_name('function_definition')
        return self.func_lst

    def get_func(self, name: str) -> list:
        rtn = []
        for _ in self.get_all_func():
            if str(_.name) == name:
                rtn.append(_)
        return rtn

    def get_all_enum(self) -> list:
        if self.enum_lst is None:
            self.enum_lst = self.get_by_type_name('enum_specifier')
        return self.enum_lst

    def get_enum(self, name: str) -> list:
        rtn = []
        for _ in self.get_all_enum():
            if str(_.name) == name:
                rtn.append(_)
        return rtn


class CFile(CCode):

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.file_content = None
        assert (os.path.exists(file_path))
        with open(file_path, 'r', errors='ignore') as r:
            self.file_content = r.read()
        super().__init__(self.file_content)
        # magic: delete #ifdef #ifndef #else #endif #elif
        # pattern = [
        #     r'#\s*if.*?\n', r'#\s*ifdef.*?\n', r'#\s*ifndef.*?\n',
        #     r'#\s*else.*?\n', r'#\s*endif.*?\n', r'#\s*elif.*?\n'
        # ]
        # pattern = [re.compile(_) for _ in pattern]
        # for _p in pattern:
        #     self.file_content = re.sub(_p, '\n', self.file_content)

        # for _p in pattern:
        #     self.file_content = re.sub(_p[0], _p[1], self.file_content)

        # manipulate self.node for more operations
