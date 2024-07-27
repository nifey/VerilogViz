import os
import sys
from pyverilog.vparser.parser import parse
import customtkinter
from verilogviz.module import *

if (len(sys.argv) < 2):
    print("No verilog input files provided")
    print("Usage: python main.py filename.v")
    exit()

filename = sys.argv[1]
with open(filename, 'r') as infile:
    code = infile.read()
ast, _ = parse([filename])

# Find the root module name and ast
basefilename = os.path.basename(filename)
rootModuleName = basefilename[:basefilename.find(".")]
rootmodule = findRootModuleAst(ast, rootModuleName)
mod = Module(rootmodule)

# Create window and display module
customtkinter.set_appearance_mode('system')
customtkinter.set_default_color_theme('blue')
root = customtkinter.CTk()
root.geometry('1000x1000')

canvas = customtkinter.CTkCanvas(root, width='1000', height='1000', bg='white')
canvas.pack()
mod.render(canvas)

root.mainloop()
