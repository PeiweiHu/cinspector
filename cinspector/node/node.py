"""
Make a wrapper of tree-sitter node
"""
import os
from tree_sitter import Language, Parser


class Util():

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
