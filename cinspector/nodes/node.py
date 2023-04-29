"""
Make a wrapper of tree-sitter node
"""

from __future__ import annotations
import os
from functools import cmp_to_key
from typing import Dict, Optional, Iterable, TYPE_CHECKING
if TYPE_CHECKING:
    from .basic_node import BasicNode
from tree_sitter import Language, Parser


class Util():
    """

    Methods:
        sort_nodes(nodes: Iterable, reverse: bool = False): sort the nodes by
            their position in internal_src.
    """

    def get_parser(self):
        abs_path = os.path.abspath(__file__)
        dire = os.path.dirname(abs_path)
        C_LANGUAGE = Language(f'{dire}/../cinspector-tree-sitter.so', 'c')
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

    @staticmethod
    def sort_nodes(nodes: Iterable, reverse: bool = False) -> Iterable:
        """ Sort the instances of BasicNode by their position in source code

        Args:
            nodes (Iterable): nodes waiting for sorting
            reverse (bool=False): use descending instead of ascending

        Return:
            sorted Iterable object
        """

        def cmp_position(node1: BasicNode, node2: BasicNode) -> int:
            if node1.start_point[0] < node2.start_point[0] or \
                    (node1.start_point[0] == node2.start_point[0] and node1.start_point[1] < node2.start_point[1]):
                return -1
            else:
                return 1

        sorted_nodes = sorted(nodes,
                              key=cmp_to_key(cmp_position),
                              reverse=reverse)
        return sorted_nodes

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


class Query():
    """ Access the specific nodes in the source code

    Query is used to access the nodes with specific properties in the
    source code. For example, find the enumeration with the type identifier
    "weekdays". To implement this, we let EnumSpecifierNode inherit from
    Query and implement the __type_identifier_result method, i.e., returns the
    field <name>. The class in interface such as CCode will gather
    all the EnumSpecifierNode and check the query method to find
    the ideal node.

    Attributes:
        mapping: a dictionary that maps the query key to the method

    Methods:
        query: query the node with the given query
    """

    def __init__(self):
        pass

    def query(self, query: Dict[str, str]) -> bool:
        """ Query the node with the given query

        Args:
            query: the query to be executed

        Returns:
            True if the node satisfies the query, otherwise False
        """
        mapping = {
            'type_identifier': self._type_identifier_result,
            'identifier': self._identifier_result,
        }

        for key, value in query.items():
            if not mapping[key]() == value:
                return False
        return True

    def _identifier_result(self) -> Optional[str]:
        raise NotImplementedError

    def _type_identifier_result(self) -> Optional[str]:
        raise NotImplementedError


class Node():
    """ The root calss of all nodes

    In general, there are three types of nodes. Node is
    the root class of all nodes while both AbstractNode
    and BasicNode are the direct children of Node.

    AbstractNode represents the logical node in the source code.
    It does not correspond to a exactly same element in the source code.
    We design AbstractNode mainly for the needs of program analysis.

    BasicNode is the base class of a series of nodes that
    correspond to the actually existing elements in the source
    code.
    """
    pass
