# cinspector

## 1. Introduction

### 1.1 What is cinspector?

**cinspector** is a static analysis framework targeting the C-based project and supports the parse, edit, analysis of the code. Based on tree-sitter, it achieves the compilation-needless analysis, which relieves the burden of configuring environment dependencies, compilation, and so on. This also enables cinspector suitable for the situations like analyzing the decompiled pseudocode.

### 1.2 What is it good for?

Any situations requiring a quick and lightweight code edit and analysis, including but not limited to:

+ Implement bug oracles for bug detection
+ Analyze the decompiler output
+ Inspect and discover the code properties for research requirements


## 2. Install

### 2.1 pip

Currently the version in the pip repository is not frequently updated. We won't recommand this way before cinspector owns a mature version.

### 2.2 local

Download this repository:

```bash
git clone https://github.com/PeiweiHu/cinspector.git
```

Build and install locally:

```bash
cd cinspector
./script/rebuild.sh
```

## 3. Usage

[Here](https://peiweihu.github.io/cinspector/) is the automatic generated documentation by sphinx. 

As a quick start, we provide a usage example that how to extract the call relationship in a source file (lets say it's foo.c) in the following. The content of foo.c is shown as below.

```c
// foo.c
#include "stdio.h"

int callee() {
    int a;
    scanf("%d", &a);
    return a;
}

void caller() {
    printf("%d\n", callee());
}

int main(void) {
    printf("%d\n", callee());
    caller();
    return 0;
}
```

First, we leverage the `CCode` in `cinspector.interfaces` to read the content for the later analysis. `CCode` can accept any code snippet.

```python
from cinspector.interfaces import CCode

with open('foo.c', 'r') as r:
    content = r.read()

cc = CCode(content) # now we get an instance of CCode
```

Now we wanna extract all function definitions in foo.c. `CCode` contains the method `get_by_type_name(type_name: str)` which can collect all nodes with the type `type_name`. The node types in cinspector are consistent with the node types in tree-sitter. You can inspect the node types with the console scipt `cinspector-parser` which is available after installing cinspector.

```bash
$ cinspector-parser -f foo.c # print the ast tree

......
FunctionDefinitionNode type=function_definition start_point=(8, 0) end_point=(10, 1) 'void caller() {    printf("%d\\n", callee());}'
......

```

We can see the function definition has the type (the attribute `node_type` in BasicNode) `function_definition`, thus we can get all function defnitions in foo.c by the following code.

```python
func_defs = cc.get_by_type_name('function_definition')
```

Let's sort the nodes in `func_defs` and check whether the first function definition is `callee`.

```python
from cinspector.nodes import *

func_defs = BasicNode.sort_nodes(func_defs)
print(func_defs[0].src)

"""
output:

int callee() {    int a;
    scanf("%d", &a);
    return a;}
"""
```

Now we need to get the call within the function definition node. There are two types of nodes in cinspector, the class `Node` is their base class. One is `BasicNode` (and subclass), representing the actual syntactic element in the source code. The other is `AbstractNode` (and subclass), which is logical and mainly for code analysis (like CFG). The function definition node `FunctionDefinitionNode` is the subclass of `BasicNode`, which owns the method `children_by_type_name(name: Union[str, List[str]])` to get all the children nodes with specific type(s) recursively. Thus, we can print the call relationship of each function definition as below.

```python
for _f in func_defs:
    callees = _f.children_by_type_name('call_expression')
    for _c in callees:
        print(f"{_f.name} invokes {_c.function}")

"""
output:

callee invokes scanf
caller invokes printf
caller invokes callee
main invokes printf
main invokes callee
main invokes caller
"""
```

All done. By the way, cinspector already provides the call graph analysis. You can find it in `cinspector.analysis`.