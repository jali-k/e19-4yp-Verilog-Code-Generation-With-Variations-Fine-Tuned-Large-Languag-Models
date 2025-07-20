# Organized Xform RAG Pipeline

A simplified, focused RAG (Retrieval-Augmented Generation) pipeline for generating Verilog transformation scripts using CodeBERT embeddings and intelligent chunking.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Vector Store

```bash
python main.py setup
```

### 3. Generate a Transformation

```bash
python main.py generate "Convert wire signals to reg signals"
```

## Directory Structure

```
xform-rag-pipeline-organized/
├── xform_rag/                 # Core pipeline package
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── embeddings.py          # CodeBERT embeddings
│   ├── document_processor.py  # Code-aware chunking
│   ├── vector_store.py        # Vector database management
│   ├── llm_manager.py         # LLM backend management
│   ├── code_generator.py      # RAG-based code generation
│   └── pipeline.py            # Main pipeline orchestration
├── xform_examples/            # Existing transformation examples
├── documentation/             # PyVerilog and pattern documentation
├── vector_store/              # Chroma vector database (created)
├── generated/                 # Generated transformation scripts (created)
├── main.py                    # CLI interface
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Usage Examples

### Command Line Interface

```bash
# Setup the system
python main.py setup -v

# Generate transformations
python main.py generate "Rename a signal throughout the module" --save
python main.py generate "Add enable signal to module inputs"

# Search for examples
python main.py search "wire to reg conversion" --count 3

# Show system statistics
python main.py stats

# Test all components
python main.py test
```

### Programmatic Usage

```python
from xform_rag import create_pipeline

# Create pipeline
pipeline = create_pipeline()

# Setup vector store (one time)
pipeline.setup_vector_store()

# Generate transformation
result = pipeline.generate_transformation("Convert wire to reg")

if result["success"]:
    print(f"Generated: {result['filename']}")
    print(result["code"])

    # Save to file
    pipeline.save_generated_code(result)
```

## Key Features

### 🧠 **CodeBERT Embeddings**

- Uses Microsoft's CodeBERT model for code-specific similarity
- Better understanding of programming constructs than general text embeddings
- 768-dimensional embeddings optimized for source code

### 📝 **Intelligent Code Chunking**

- Respects Python class and function boundaries
- Preserves code context with smart separators
- Smaller chunks (1500 chars) for better precision
- 10% overlap to maintain context continuity

### 🎯 **Focused Design**

- No caching or complex optimizations
- Clear, maintainable code structure
- Purpose-built for transformation generation quality
- Simple error handling and logging

### 📚 **Comprehensive Knowledge Base**

- Existing transformation examples from `xform_examples/`
- PyVerilog AST documentation
- Transformation pattern library
- Best practices and common approaches

## Documentation Setup Guide

The pipeline requires PyVerilog documentation to be placed in the `documentation/` directory. Follow the guide in `documentation/PYVERILOG_DOCS_GUIDE.md` to:

1. Collect PyVerilog AST documentation
2. Create transformation pattern guides
3. Add setup and usage examples

Sample documentation files are already provided:

- `pyverilog_ast_nodes.md` - AST node reference
- `transformation_patterns.md` - Common patterns

## Configuration

The system uses `RAGConfig` for all settings:

```python
@dataclass
class RAGConfig:
    # Directories
    xform_examples_dir: Path = Path("./xform_examples")
    documentation_dir: Path = Path("./documentation")
    vector_store_dir: Path = Path("./vector_store")
    output_dir: Path = Path("./generated")

    # Model settings
    model_type: str = "ollama"
    model_name: str = "qwen2.5-coder:1.5b"

    # Embedding settings
    embedding_model: str = "microsoft/codebert-base"

    # Chunking settings
    chunk_size: int = 1500
    chunk_overlap: int = 150

    # Retrieval settings
    retrieval_k: int = 3

    # Generation settings
    temperature: float = 0.1
    max_tokens: int = 2048
```

## Components Overview

### `embeddings.py` - CodeBERT Implementation

- Direct CodeBERT integration using transformers
- Handles tokenization and embedding generation
- Optimized for code understanding

### `document_processor.py` - Smart Chunking

- Code-aware text splitting
- Metadata enrichment for better retrieval
- Support for multiple document types

### `vector_store.py` - Vector Database

- Chroma integration with CodeBERT embeddings
- Simple setup and retrieval
- Basic statistics and management

### `code_generator.py` - RAG Generation

- Retrieval-augmented generation using LangChain
- Focused prompt template for transformations
- Clean result formatting

### `pipeline.py` - Main Orchestration

- Simple component coordination
- Error handling and logging
- System testing and statistics

## Dependencies

### Core Requirements

- `langchain` - RAG pipeline framework
- `transformers` - CodeBERT model access
- `torch` - Neural network backend
- `chromadb` - Vector database
- `pyverilog` - Verilog AST parsing

### Optional

- `sentence-transformers` - Alternative embeddings
- `numpy` - Numerical operations

## Troubleshooting

### Common Issues

1. **Vector store creation fails**

   - Ensure `xform_examples/` contains Python files
   - Check that CodeBERT model downloads successfully
   - Verify write permissions for `vector_store/` directory

2. **LLM connection errors**

   - Ensure Ollama is running with the specified model
   - Check model name matches available models
   - Verify network connectivity for model downloads

3. **Memory issues with CodeBERT**
   - CodeBERT requires ~1GB RAM for embeddings
   - Consider using CPU-only mode for compatibility
   - Monitor memory usage during vector store creation

### Debug Mode

Run with verbose logging:

```bash
python main.py setup --verbose
python main.py generate "your request" --verbose
```

## Limitations

- Requires Ollama or EC2 endpoint for LLM access
- CodeBERT model needs ~1GB memory for embeddings
- No built-in caching (by design for simplicity)
- Limited to Python-based transformation scripts
- Basic error handling without recovery mechanisms

---

_This pipeline prioritizes code generation quality and simplicity over performance optimizations._
