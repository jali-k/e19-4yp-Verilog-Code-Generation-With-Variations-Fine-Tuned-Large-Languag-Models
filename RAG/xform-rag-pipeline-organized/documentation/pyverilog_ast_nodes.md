# PyVerilog AST Nodes Reference

This document provides a reference for PyVerilog AST nodes commonly used in Verilog transformations.

## Core Node Types

### ModuleDef

Represents a Verilog module definition.

**Attributes:**

- `name`: Module name (string)
- `paramlist`: Parameter list
- `portlist`: Port list
- `items`: Module items (declarations, always blocks, etc.)

**Usage:**

```python
if isinstance(node, ModuleDef):
    module_name = node.name
    # Process module contents
```

### Decl

Represents variable declarations (wire, reg, integer, etc.).

**Attributes:**

- Contains a list of declaration items

**Usage:**

```python
if isinstance(node, Decl):
    for item in node.children():
        if isinstance(item, Wire):
            # Process wire declaration
        elif isinstance(item, Reg):
            # Process reg declaration
```

### Wire

Represents wire declarations.

**Attributes:**

- `name`: Wire name
- `width`: Width specification (if any)

### Reg

Represents register declarations.

**Attributes:**

- `name`: Register name
- `width`: Width specification (if any)

### Identifier

Represents signal/variable names in expressions.

**Attributes:**

- `name`: The identifier name

**Usage:**

```python
if isinstance(node, Identifier):
    signal_name = node.name
    # Check if this is the signal we want to rename
```

### Width

Represents bit width specifications.

**Attributes:**

- `msb`: Most significant bit
- `lsb`: Least significant bit

### Always

Represents always blocks.

**Attributes:**

- `sens_list`: Sensitivity list
- `statement`: Block statement

### IfStatement

Represents if-else statements.

**Attributes:**

- `cond`: Condition expression
- `true_statement`: Statement for true case
- `false_statement`: Statement for false case

## Common Traversal Patterns

### Basic AST Traversal

```python
def visit(self, node):
    # Process current node
    if isinstance(node, SomeNodeType):
        # Handle this node type
        pass

    # Visit all children
    for child in node.children():
        self.visit(child)
```

### Finding Specific Elements

```python
def find_signals(self, node):
    if isinstance(node, Decl):
        for item in node.children():
            if isinstance(item, Wire):
                self.wire_signals.append(item.name)
            elif isinstance(item, Reg):
                self.reg_signals.append(item.name)

    # Continue traversal
    for child in node.children():
        self.find_signals(child)
```
