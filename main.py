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

# Width and Height for Window, Pane and Canvas
window_width=1500
window_height=800
text_pane_width = 500
canvas_pane_width = 1000
pane_height = window_height
canvas_width = 1000
canvas_height = pane_height

# Create window and display module
customtkinter.set_appearance_mode('system')
customtkinter.set_default_color_theme('blue')

root = customtkinter.CTk()
root.resizable(0,0)
root.rowconfigure(0, weight=1)
root.title('VerilogViz (' + filename + ')')
root.geometry(f'{window_width}x{window_height}')

#=====================================================
# Canvas pane on the right
#=====================================================
canvas_pane = customtkinter.CTkScrollableFrame(root, width=canvas_pane_width, height=pane_height, orientation="horizontal")
canvas_pane.grid(row=0, column=1)
canvas = customtkinter.CTkCanvas(canvas_pane, width=canvas_width, height=canvas_height, bg='white')
canvas.pack(fill='both')

#=====================================================
# Text pane on the left
#=====================================================
text_pane = customtkinter.CTkFrame(root, width=text_pane_width, height=pane_height)
text_pane.grid(row=0, column=0, sticky='ns')
button_height = 20
button_width = 100

menu_bar_height = button_height + 5
menu_bar = customtkinter.CTkFrame(text_pane, width=text_pane_width, height=menu_bar_height)
menu_bar.pack(fill='both')

textbox = customtkinter.CTkTextbox(text_pane, wrap='none', width=text_pane_width, height=pane_height)
textbox.insert('0.0', code)
textbox.pack(fill='both')

combobox = customtkinter.CTkComboBox(menu_bar, values=[], corner_radius=0)
combobox.grid(row=0, column=2)

modules_in_file = []
moduleDefs = []

def render_file():
    try:
        ast, _ = parse([filename])
    except Exception as e:
        dialog = customtkinter.CTkInputDialog()
        dialog.title("Compilation error")
        dialog.geometry("400x400")
        customtkinter.CTkLabel(dialog, text=str(e)).pack()
        dialog.mainloop()
    global moduleDefs
    moduleDefs = get_modules_from_ast(ast)
    global modules_in_file
    modules_in_file = list(map(lambda x: x.name, moduleDefs))
    selected_module_name = combobox.get()
    combobox.configure(values = modules_in_file)
    if selected_module_name not in modules_in_file:
        selected_module_name = moduleDefs[0].name
        combobox.set(selected_module_name)
    render_module(selected_module_name)

def render_module(selected_module_name):
    for item in canvas.find_all():
        canvas.delete(item)
    module_to_render = None
    for module in moduleDefs:
        if module.name == selected_module_name:
            module_to_render = module
            break
    if module_to_render == None: return
    module = Module(module_to_render,
                        canvas_width, canvas_height)
    module.render(canvas)
    del module
combobox.configure(command=render_module)

def save_file():
    newcode = textbox.get('0.0', 'end')
    with open(filename, 'w') as outputfile:
        outputfile.write(newcode)
    render_file()

save_button = customtkinter.CTkButton(menu_bar, corner_radius=0, border_width=0, height=button_height, width=button_width, text="Save", command=save_file)
save_button.grid(row=0, column=0)
customtkinter.CTkLabel(menu_bar, text=" Module to render:").grid(row=0, column=1)

render_file()
root.mainloop()
