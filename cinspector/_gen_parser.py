import subprocess
from tree_sitter import Language

subprocess.check_call([
    'git', 'clone', '-b', 'v0.20.2',
    'https://github.com/tree-sitter/tree-sitter-c.git'
])
Language.build_library('cinspector-tree-sitter.so', ['tree-sitter-c'])
