___
# HDL Code Generation using LLMs
___

The increasing complexity of modern hardware systems necessitates more efficient verification
processes to ensure functional correctness. Traditional test case generation for Verilog designs is
manual, time-consuming, and prone to human error, making automation essential. This project
aims to automate Verilog code variation generation to enhance hardware design verification,
leveraging Large Language Models (LLMs) and structured transformation techniques.
The first phase involves identifying the most effective open-source LLMs from available
literature, which can surpass the state-of-the-art model performances in recognized benchmarks.
The selected models will then be used to generate Verilog code variations through three
structured approaches: (1) Python-based transformations, where variations are applied to a
Python implementation that can be converted to Verilog using PyVerilog and output the Python
implementation with the variations, and (2) Direct Verilog transformations, where modifications
are applied directly to Verilog code and output the Verilog code with the variations. (3) Generate
X-Form functions, which are Python scripts that can be transformed based on Verilog
implementations using variations described as a Python script using an object module; the bestperforming approach will be selected as the final deliverable.
If the chosen model fails to generate syntactically and functionally correct variations, an
additional phase will be conducted to improve Verilog code generation from natural language
problem descriptions. This will involve dataset preparation and model fine-tuning to generate
both Verilog and Python (Pyverilog) implementations, and then again fine-tuning models to
generate variations.
The implementation involves dataset construction, LLM fine-tuning (Supervised Fine-Tuning),
and evaluation against predefined correctness metrics. The final deliverable will be a fine-tuned
LLM that can be used to automate the Verilog variation generation using the most effective
approach. This system aims to significantly reduce manual effort and errors in hardware design
verification, improving efficiency in Electronic Design Automation (EDA) workflows.
