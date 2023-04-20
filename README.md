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

Install the prerequisites:

```bash
pip install tree-sitter, networkx
```

Build and install locally:

```bash
cd cinspector
./script/rebuild.sh
```

## Usage

[Here](https://peiweihu.github.io/cinspector/) is the automatic generated documentation by sphinx. 

As a quick start, we provide a usage example that how to extract the call relationship in a source file (lets say it's foo.c) in the following.