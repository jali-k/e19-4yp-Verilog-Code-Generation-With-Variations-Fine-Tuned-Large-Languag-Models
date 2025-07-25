# Generated by Ollama Llama 3
# Task: signal_rename_minimal
# Attempt: 6
# Success: False
# Overall Score: 0.485

import sys
sys.path.append('../')
from veriloggen import *

import pyverilog.ast as ast
import re

class RenameSignal(ast.NodeVisitor):

  def __init__(self, old_name, new_name):
    self.old_name = old_name 
    self.new_name = new_name 

  def visit_Declaration(self, node): # Visit declarations and replace the signal name with the new one.
    if not isinstance(node.signal, ast.SignalName) or node.signal.name != self.old_name:
      return node
    else: 
      return Declaration(signal=ast.SignalName(name=self.new_name))

  def visit_Statement(self, node): # Visit statement and replace all references to the signal with the new name.
    if isinstance(node.left, ast.SignalRef) and node.left.signal_name.name == self.old_name:
      node.left = SignalRef(ast.SignalName(name=self.new_name))
    for child in node.children:
      node.append(child.accept(self))

  def visit_Expression(self, node): # Visit expression and replace all references to the signal with the new name.
    if isinstance(node.left, ast.SignalRef) and node.left.signal_name.name == self.old_name:
      node.left = SignalRef(ast.SignalName(name=self.new_name))
    for child in node.children:
      node.append(child.accept(self))

  def visit_Reference(self, node): # Visit reference and replace all references to the signal with the new name.
    if isinstance(node.signal_ref, ast.SignalRef) and node.signal_ref.signal_name.name == self.old_name:
      node.signal_ref = SignalRef(ast.SignalName(name=self.new_name))
    for child in node.children:
      node.append(child.accept(self))

  def visit_Reg(self, node): # Visit reg and replace the signal name with the new one.
    if not isinstance(node.ref, ast.RegRef) or node.ref.signal_name.name != self.old_name:
      return node
    else: 
      return Reg(ref=RegRef(ast.SignalName(name=self.new_name)))

  def visit_Module(self, node): # Visit module and replace all references to the signal with the new name.
    for child in node.children:
      node.append(child.accept(self))

  def transform(self, ast_node):
    self.visit(ast_node)
    return ast_node

def xform_rename_signal(old_name, new_name):

  class RenameSignalVisitor(RenameSignal):
    def __init__(self):
      super().__init__(old_name=old_name, new_name=new_name)

  parser = argparse.ArgumentParser()
  parser.add_argument('file', type=str)
  args = parser.parse_args()

  # Read in the file and parse it using PyVerilog
  with open(args.file) as f:
    contents = f.read()
  ast_node = ast.parse(contents)
  
  vlog_name = RenameSignalVisitor().transform(ast_node)

  return vlog_name