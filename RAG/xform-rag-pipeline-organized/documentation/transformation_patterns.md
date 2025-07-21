# Transformation Patterns

Common patterns for implementing Verilog code transformations using PyVerilog AST analysis and regex modifications.

## Pattern 1: Signal Type Conversion (Wire to Reg)

### Approach

1. Use PyVerilog AST to identify wire declarations
2. Use regex to replace wire keywords with reg keywords

### Implementation

```python
class WireToRegTransform:
    def __init__(self):
        self.wire_signals = []

    def visit(self, node):
        if isinstance(node, Decl):
            for item in node.children():
                if isinstance(item, Wire):
                    self.wire_signals.append(item.name)

        for child in node.children():
            self.visit(child)

    def apply_regex_transform(self, content):
        for signal in self.wire_signals:
            # Replace wire declaration
            pattern = r'\bwire\s+' + re.escape(signal) + r'\b'
            content = re.sub(pattern, f'reg {signal}', content)
        return content
```

## Pattern 2: Signal Renaming

### Approach

1. Find all occurrences of target signal using AST
2. Use regex to replace all instances consistently

### Implementation

```python
class SignalRenameTransform:
    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name
        self.found_signal = False

    def visit(self, node):
        if isinstance(node, Identifier):
            if node.name == self.old_name:
                self.found_signal = True

        for child in node.children():
            self.visit(child)

    def apply_regex_transform(self, content):
        if self.found_signal:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(self.old_name) + r'\b'
            content = re.sub(pattern, self.new_name, content)
        return content
```

## Pattern 3: Module Name Change

### Approach

1. Identify module definition using AST
2. Replace module name in declaration and endmodule

### Implementation

```python
class ModuleRenameTransform:
    def __init__(self, new_name):
        self.new_name = new_name
        self.old_name = None

    def visit(self, node):
        if isinstance(node, ModuleDef):
            self.old_name = node.name

        for child in node.children():
            self.visit(child)

    def apply_regex_transform(self, content):
        if self.old_name:
            # Replace module declaration
            pattern = r'module\s+' + re.escape(self.old_name) + r'\b'
            content = re.sub(pattern, f'module {self.new_name}', content)

            # Replace endmodule comment if present
            pattern = r'endmodule\s*//\s*' + re.escape(self.old_name)
            content = re.sub(pattern, f'endmodule // {self.new_name}', content)

        return content
```

## Pattern 4: Signal Width Transformation

### Approach

1. Use PyVerilog AST to identify signal declarations with specific widths
2. Use regex to replace width specifications in wire/reg declarations
3. Handle both packed and unpacked array dimensions

### Implementation

```python
class SignalWidthTransform:
    def __init__(self, signal_name, new_width):
        self.signal_name = signal_name
        self.new_width = new_width
        self.found_signal = False
        self.original_width = None

    def visit(self, node):
        # Check for wire or reg declarations
        if isinstance(node, Wire) or isinstance(node, Reg):
            if node.name == self.signal_name:
                self.found_signal = True
                if node.width:
                    # Extract original width from AST
                    self.original_width = self._extract_width(node.width)

        for child in node.children():
            self.visit(child)

    def _extract_width(self, width_node):
        # Extract width from AST width node (e.g., [7:0] -> 8)
        if hasattr(width_node, 'msb') and hasattr(width_node, 'lsb'):
            return width_node.msb.value - width_node.lsb.value + 1
        return None

    def apply_regex_transform(self, content):
        if self.found_signal:
            # Pattern for wire/reg with width specification
            # Match: wire [7:0] signal_name or reg [15:0] signal_name
            old_msb = self.new_width - 1 if self.original_width else 7
            new_msb = self.new_width - 1

            # Replace width in signal declaration
            pattern = rf'\b(wire|reg)\s*\[\s*\d+\s*:\s*0\s*\]\s+{re.escape(self.signal_name)}\b'
            replacement = rf'\1 [{new_msb}:0] {self.signal_name}'
            content = re.sub(pattern, replacement, content)

        return content
```

## Pattern 5: Port Width Modification

### Approach

1. Find module definition and its ports using AST
2. Identify target port in port list
3. Update port width in module declaration

### Implementation

```python
class PortWidthTransform:
    def __init__(self, port_name, new_width):
        self.port_name = port_name
        self.new_width = new_width
        self.found_port = False

    def visit(self, node):
        if isinstance(node, ModuleDef):
            for port in node.portlist.ports:
                if hasattr(port, 'name') and port.name == self.port_name:
                    self.found_port = True

        for child in node.children():
            self.visit(child)

    def apply_regex_transform(self, content):
        if self.found_port:
            new_msb = self.new_width - 1
            # Match port declarations: input [7:0] port_name or output [15:0] port_name
            pattern = rf'\b(input|output|inout)\s*\[\s*\d+\s*:\s*0\s*\]\s+{re.escape(self.port_name)}\b'
            replacement = rf'\1 [{new_msb}:0] {self.port_name}'
            content = re.sub(pattern, replacement, content)

        return content
```

## Pattern 4: Port Addition

### Approach

1. Analyze module ports using AST
2. Use regex to insert new port in appropriate location

### Implementation

```python
class AddPortTransform:
    def __init__(self, port_name, port_type="input"):
        self.port_name = port_name
        self.port_type = port_type
        self.module_found = False

    def visit(self, node):
        if isinstance(node, ModuleDef):
            self.module_found = True

        for child in node.children():
            self.visit(child)

    def apply_regex_transform(self, content):
        if self.module_found:
            # Find the last port and add new one
            pattern = r'(\s*input\s+\w+\s*,|\s*output\s+\w+\s*,|\s*inout\s+\w+\s*,)'
            def replacer(match):
                return match.group(1) + f'\n    {self.port_type} {self.port_name},'

            # Add to the last port (this is simplified)
            content = re.sub(pattern, replacer, content, count=1)

        return content
```

## Best Practices

### 1. Two-Phase Approach

- **Phase 1**: AST Analysis - Understand code structure
- **Phase 2**: Regex Transformation - Make actual changes

### 2. Error Handling

```python
def transform_with_error_handling(input_file, output_file):
    try:
        # Parse with PyVerilog
        ast, directives = parse([input_file])

        # Read original content
        with open(input_file, 'r') as f:
            content = f.read()

        # Apply transformation
        transformer = SomeTransform()
        transformer.visit(ast)
        new_content = transformer.apply_regex_transform(content)

        # Write result
        with open(output_file, 'w') as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"Transformation failed: {e}")
        return False
```

### 3. Validation

Always validate that the transformation preserves syntax:

```python
def validate_transformation(output_file):
    try:
        parse([output_file])
        return True
    except:
        return False
```
