# Verilog Code Generation with Variations Using Fine-Tuned Large Language Models

## Project Overview
This Final Year Project (FYP) focuses on generating Verilog code and its variations using fine-tuned Large Language Models (LLMs). The project leverages natural language prompts and base Verilog implementations to create syntactically correct and diverse Verilog code variations. Three distinct approaches are explored: PyVerilog-based variation generation, native Verilog-based variation generation, and X-Form-based transformation generation. The project includes data extraction, dataset creation, model fine-tuning, and evaluation to identify the most effective approach for Verilog code generation.

## Objectives
- **Data Extraction and Curation**: Extract Verilog and PyVerilog code from GitHub and textbooks, curate datasets, and ensure syntactic correctness using tools like Verilator.
- **Dataset Creation**: Develop base implementation datasets and generate variations in Verilog, PyVerilog, and X-Form formats, validated using VCS and VCS SpyGlass.
- **Model Fine-Tuning**: Fine-tune LLMs using three methods (Direct PEFT, Agentic RAG, and Mixture of Experts) to generate Verilog code and variations from natural language prompts.
- **Evaluation and Ranking**: Evaluate and rank LLMs based on correctness, diversity, and complexity of generated Verilog code and variations.
- **Comparative Analysis**: Analyze the performance of the three approaches to determine the most effective method for Verilog code generation with variations.

## Project Roadmap
The project is structured into a 12-week timeline, with specific tasks and deliverables for each phase:

### Week 1: Data Extraction and Base Dataset Creation
- **Tasks**:
  - Extract Verilog code from GitHub using Google BigQuery and from textbooks using PyMuPDF.
  - Apply data curation techniques to clean and preprocess extracted code.
  - Perform syntax checking using Verilator.
  - Finalize the "Base Implementations" dataset, including problem descriptions and corresponding Verilog/PyVerilog implementations.
- **Deliverables**:
  - Extracted and curated Verilog/PyVerilog codes.
  - Test results from Verilator syntax checking.
  - Finalized "Base Implementations" dataset.

### Week 2: Variations Dataset Creation
- **Tasks**:
  - Generate Verilog variations according to the provided test plan, validated with VCS/VCS SpyGlass.
  - Generate PyVerilog variations using Python scripts, validated with VCS/VCS SpyGlass.
  - Generate X-Form transformations, apply them to create Verilog variations, and validate with VCS/VCS SpyGlass.
- **Deliverables**:
  - Test results for all variation datasets.
  - Finalized "Variations" datasets (Verilog, PyVerilog, X-Forms).

### Weeks 3–4: Model Evaluation and Ranking
- **Tasks**:
  - Design prompts for Verilog code and variation generation.
  - Use LLMs (e.g., GPT, CodeT5, StarCoder) to generate outputs.
  - Fine-tune models using Parameter Efficient Fine-Tuning (PEFT) on Verilog and PyVerilog generation tasks.
  - Define evaluation metrics (correctness, diversity, complexity).
  - Score and rank model outputs.
- **Deliverables**:
  - Evaluation report on model performance for Verilog and PyVerilog generation.
  - Ranked list of models based on performance.

### Weeks 5–6: Approach 1 – PyVerilog-Based Variation Generation
- **Tasks**:
  - Use PyVerilog scripts and natural language (NL) prompts to generate PyVerilog variations.
  - Fine-tune LLMs using a dataset of base Verilog code and NL prompts.
  - Implement three fine-tuning methods: Direct PEFT, Agentic RAG, and Mixture of Experts.
  - Convert generated PyVerilog code to Verilog using PyVerilog tools.
  - Validate outputs using VCS/VCS SpyGlass.
- **Deliverables**:
  - Trained models for PyVerilog-based variation generation.
  - Results from the three fine-tuning methods.
  - Progress reports from VCS/VCS SpyGlass testing.

### Weeks 7–8: Approach 2 – Native Verilog-Based Variation Generation
- **Tasks**:
  - Train LLMs to directly generate Verilog variations using NL prompts.
  - Fine-tune models using three methods: Direct PEFT, Agentic RAG, and Mixture of Experts.
  - Address low data volume through data augmentation (e.g., mutation, combination, randomization).
  - Validate synthetic data and model outputs using VCS/VCS SpyGlass.
- **Deliverables**:
  - Trained models for native Verilog-based variation generation.
  - Results from the three fine-tuning methods.
  - Ongoing test results from VCS/VCS SpyGlass.

### Weeks 9–10: Approach 3 – X-Form Generation from NL Prompts
- **Tasks**:
  - Train LLMs to generate X-Form transformation instructions from NL prompts.
  - Validate X-Form syntax and logic.
  - Implement three fine-tuning methods: Direct PEFT, Agentic RAG, and Mixture of Experts.
  - Apply X-Forms to base Verilog code to generate variations.
  - Validate outputs using VCS/VCS SpyGlass.
- **Deliverables**:
  - Trained models for X-Form generation.
  - Results from the three fine-tuning methods.
  - Test results from VCS/VCS SpyGlass.

### Week 11: Analysis and Finalization
- **Tasks**:
  - Analyze evaluation results from all three approaches.
  - Identify the most effective approach for Verilog code generation with variations.
  - Document model performance, dataset impact, and recommendations.
- **Deliverables**:
  - Final report on the best approach(es).
  - Comparative evaluation summary.
  - Recommendations for future improvements.

### Week 12: Improvements and Final Submission
- **Tasks**:
  - Implement improvements based on feedback.
  - Finalize the system and documentation.
- **Deliverables**:
  - Final model/system.
  - Comprehensive project documentation.

## Tools and Technologies
- **Data Extraction**:
  - **Google BigQuery**: For extracting Verilog code from GitHub.
  - **PyMuPDF**: For extracting Verilog code from textbooks.
- **Syntax Checking and Validation**:
  - **Verilator**: For syntax checking of Verilog code.
  - **VCS/VCS SpyGlass**: For testing and validating Verilog and PyVerilog variations.
  - **PyVerilog**: For generating and converting PyVerilog code to Verilog.
- **Model Training and Fine-Tuning**:
  - **Large Language Models**: GPT, CodeT5, StarCoder.
  - **Fine-Tuning Methods**: Direct PEFT, Agentic RAG, Mixture of Experts.
- **Programming Languages**:
  - Python (for PyVerilog and scripting).
  - Verilog (for native code and variations).
- **Data Augmentation**:
  - Techniques like mutation, combination, and randomization for synthetic data generation.

## Team
- Sahan Nimantha (E/19/205, <email>)</email>
- Jaliya Kumarasiri (E/19/210, <email>)</email>
- Vidura Yashan (E/19/455, <email>)</email>

## Supervisors
- Dr. Isuru Nawinne (<email>)</email>
- Prof. Roshan G. Ragel (<email>)</email>
- Dr. Damayanthi Herath (<email>)</email>
