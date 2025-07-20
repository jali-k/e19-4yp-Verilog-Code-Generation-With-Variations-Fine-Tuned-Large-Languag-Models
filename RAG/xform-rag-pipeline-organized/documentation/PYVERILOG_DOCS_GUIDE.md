# PyVerilog Documentation Collection Guide

## Required Documentation Sources

To properly populate the knowledge base for Verilog transformation generation, you need to collect the following PyVerilog documentation files:

### 1. PyVerilog AST Node Reference

**Location**: Create this file manually based on PyVerilog source code
**Filename**: `pyverilog_ast_nodes.md`

**Content to include**:

- All AST node classes from `pyverilog.vparser.ast`
- Node attributes and their meanings
- Common usage patterns for each node type
- Examples of how to identify and work with each node

**How to generate**:

```python
import pyverilog.vparser.ast as ast
import inspect

# Get all AST node classes
ast_classes = [cls for name, cls in inspect.getmembers(ast) if inspect.isclass(cls)]
# Document each class with its attributes and methods
```

### 2. PyVerilog Parser Documentation

**Location**: From PyVerilog repository or documentation
**Filename**: `pyverilog_parser.md`

**Content to include**:

- How to use `parse()` function
- Handling parser output (AST + directives)
- Common parsing patterns
- Error handling

### 3. Transformation Patterns

**Location**: Create from existing xform examples
**Filename**: `transformation_patterns.md`

**Content to include**:

- Common transformation patterns
- Best practices for AST traversal
- Regex patterns for code modification
- Error handling strategies

### 4. PyVerilog Installation and Setup

**Location**: PyVerilog documentation
**Filename**: `pyverilog_setup.md`

**Content to include**:

- Installation requirements
- Dependencies
- Basic usage examples

## File Collection Commands

### Option 1: From PyVerilog Repository

```bash
# Clone PyVerilog repository
git clone https://github.com/PyHDI/Pyverilog.git
# Copy relevant documentation files to ./documentation/
```

### Option 2: Generate from Installed PyVerilog

```python
# Generate AST documentation programmatically
python generate_ast_docs.py > documentation/pyverilog_ast_nodes.md
```

### Option 3: Manual Creation

Create the documentation files manually based on:

- PyVerilog source code
- Existing xform examples
- PyVerilog README and documentation

## Directory Structure After Collection

```
documentation/
├── PYVERILOG_DOCS_GUIDE.md (this file)
├── pyverilog_ast_nodes.md
├── pyverilog_parser.md
├── transformation_patterns.md
├── pyverilog_setup.md
└── code_examples.md
```

## Next Steps

1. Collect the documentation files as described above
2. Place them in the `documentation/` directory
3. Run the RAG pipeline setup to process these files
4. The documentation will be automatically chunked and embedded using CodeBERT
