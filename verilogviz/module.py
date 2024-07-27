from pyverilog.vparser.ast import *
import customtkinter
import random

def find_root_module_ast(currentAst, rootModuleName):
    """ Traverses the AST tree and returns the ModuleDef node with the given module name"""
    if isinstance(currentAst, Source) or isinstance(currentAst, Description):
        for child in currentAst.children():
            returnVal = find_root_module_ast(child, rootModuleName)
            if returnVal != None:
                return returnVal
    elif isinstance(currentAst, ModuleDef):
        return currentAst
    return None

def get_module_items(moduleAst):
    """ Returns a list of all wires and instances present in a module definition"""
    assert isinstance(moduleAst, ModuleDef)
    wire_list = []
    instance_list = []
    for item in moduleAst.items:
        if isinstance(item, Decl):
            wire_list.extend(item.children())
        elif isinstance(item, InstanceList):
            instance_list.extend(item.children())
        else: assert False
    return wire_list, instance_list

gate_bubble_width = 10
gate_gap_width = 10
gate_xor_gap_width = 5
gate_buf_height = 30
gate_buf_width = 40
standard_modules = ['and', 'or', 'buf', 'not', 'nand', 'nor', 'xor', 'xnor']
def render_and_gate(canvas, start_x, start_y, end_x, end_y):
    mid_x = (start_x + end_x)/2
    canvas.create_line(start_x, start_y, start_x, end_y)
    canvas.create_line(start_x, start_y, mid_x, start_y)
    canvas.create_line(start_x, end_y, mid_x, end_y)
    canvas.create_arc(start_x, start_y, end_x, end_y, start=-90, extent=180, style='arc')
def render_nand_gate(canvas, start_x, start_y, end_x, end_y):
    end_x = end_x - gate_bubble_width
    render_and_gate(canvas, start_x, start_y, end_x, end_y)
    canvas.create_oval(end_x, (start_y + end_y)/2 - gate_bubble_width/2,
                       end_x + gate_bubble_width, (start_y + end_y)/2 + gate_bubble_width/2)
def render_or_gate(canvas, start_x, start_y, end_x, end_y):
    canvas.create_arc(start_x - gate_gap_width, end_y,
                      start_x + gate_gap_width, start_y,
                      start=-90, extent=180, style='arc')
    canvas.create_arc(start_x - (end_x - start_x), start_y,
                      end_x, end_y, start=0,
                      extent=90, style='arc')
    canvas.create_arc(start_x - (end_x - start_x), start_y,
                      end_x, end_y,
                      start=-90, extent=90, style='arc')
def render_nor_gate(canvas, start_x, start_y, end_x, end_y):
    end_x = end_x - gate_bubble_width
    render_or_gate(canvas, start_x, start_y, end_x, end_y)
    canvas.create_oval(end_x, (start_y + end_y)/2 - gate_bubble_width/2,
                       end_x + gate_bubble_width, (start_y + end_y)/2 + gate_bubble_width/2)
def render_xor_gate(canvas, start_x, start_y, end_x, end_y):
    start_x = start_x + gate_xor_gap_width
    canvas.create_arc(start_x - gate_xor_gap_width - gate_gap_width, end_y,
                      start_x - gate_xor_gap_width + gate_gap_width, start_y,
                      start=-90, extent=180, style='arc')
    render_or_gate(canvas, start_x, start_y, end_x, end_y)
def render_xnor_gate(canvas, start_x, start_y, end_x, end_y):
    start_x = start_x + gate_xor_gap_width
    canvas.create_arc(start_x - gate_xor_gap_width - gate_gap_width, end_y,
                      start_x - gate_xor_gap_width + gate_gap_width, start_y,
                      start=-90, extent=180, style='arc')
    render_nor_gate(canvas, start_x, start_y, end_x, end_y)
def render_buf_gate(canvas, start_x, start_y, end_x, end_y):
    width = end_x - start_x
    height = end_y - start_y
    start_x = start_x + width/2 - gate_buf_width/2
    end_x = end_x - width/2 + gate_buf_width/2
    start_y = start_y + height/2 - gate_buf_height/2
    end_y = end_y - height/2 + gate_buf_height/2
    mid_x = (start_x + end_x)/2
    mid_y = (start_y + end_y)/2
    canvas.create_line(start_x, start_y, start_x, end_y)
    canvas.create_line(start_x, start_y, end_x, mid_y)
    canvas.create_line(start_x, end_y, end_x, mid_y)
def render_not_gate(canvas, start_x, start_y, end_x, end_y):
    width = end_x - start_x
    height = end_y - start_y
    start_x = start_x + width/2 - gate_buf_width/2
    end_x = end_x - width/2 + gate_buf_width/2
    start_y = start_y + height/2 - gate_buf_height/2
    end_y = end_y - height/2 + gate_buf_height/2
    mid_x = (start_x + end_x)/2
    mid_y = (start_y + end_y)/2
    canvas.create_line(start_x, start_y, start_x, end_y)
    canvas.create_line(start_x, start_y, end_x, mid_y)
    canvas.create_line(start_x, end_y, end_x, mid_y)
    canvas.create_oval(end_x, mid_y - gate_bubble_width/2,
                       end_x + gate_bubble_width, mid_y + gate_bubble_width/2)

def render_standard_instance(canvas, instance, center_x, center_y, width=100, height=100):
    start_x = center_x - width/2
    start_y = center_y - height/2
    end_x = center_x + width/2
    end_y = center_y + height/2
    match instance.module:
        case 'and':     render_and_gate(canvas, start_x, start_y, end_x, end_y)
        case 'nand':    render_nand_gate(canvas, start_x, start_y, end_x, end_y)
        case 'or':      render_or_gate(canvas, start_x, start_y, end_x, end_y)
        case 'nor':     render_nor_gate(canvas, start_x, start_y, end_x, end_y)
        case 'xor':     render_xor_gate(canvas, start_x, start_y, end_x, end_y)
        case 'xnor':    render_xnor_gate(canvas, start_x, start_y, end_x, end_y)
        case 'not':     render_not_gate(canvas, start_x, start_y, end_x, end_y)
        case 'buf':     render_buf_gate(canvas, start_x, start_y, end_x, end_y)
        case _:         assert False

def render_instance(canvas, instance, center_x, center_y, width=50, height=50):
    """ Renders the given instance on the canvas centered at position (center_x, center_y)"""
    assert isinstance(instance, Instance)
    if instance.module in standard_modules:
        render_standard_instance(canvas, instance, center_x, center_y, width, height)
    else:
        canvas.create_rectangle(center_x - width/2, center_y - height/2,
                                center_x + width/2, center_y + height/2)

class Module():
    def __init__(self, ast_node):
        self.ast = ast_node
        self.name = ast_node.name
        self.input_ports = []
        self.output_ports = []
        for port in ast_node.portlist.children():
            assert isinstance(port, Ioport)
            assert len(port.children()) == 1
            port = port.children()[0]
            if isinstance(port, Input):
                self.input_ports.append(port)
            elif isinstance(port, Output):
                self.output_ports.append(port)
            else: assert False
        self.wires, self.instances = get_module_items(self.ast)

    def __str__(self):
        return self.name

    def render(self, canvas):
        canvas_width = 1000
        canvas_height = 1000
        module_width = 800
        module_height = 800
        module_start_x = (canvas_width/2) - (module_width/2)
        module_end_x = (canvas_width/2) + (module_width/2)
        module_start_y = (canvas_height/2) - (module_height/2)
        module_end_y = (canvas_height/2) + (module_height/2)
        canvas.create_rectangle(module_start_x, module_start_y, module_end_x, module_end_y)

        # Display root module name
        text_height = 20
        canvas.create_text((module_start_x + module_end_x)/2,
                           module_start_y - text_height, text = self.name)

        port_length = 10
        text_length = 20

        # Place input ports equidistant from each other on left edge of module box
        num_input_ports = len(self.input_ports)
        input_port_shift = module_height/(num_input_ports + 1)
        current_port_y = module_start_y + input_port_shift
        for port in self.input_ports:
            canvas.create_rectangle(module_start_x - port_length,
                                    current_port_y - (port_length/2),
                                    module_start_x,
                                    current_port_y + (port_length/2))
            canvas.create_text(module_start_x - port_length - text_length,
                               current_port_y,
                               text=port.name)
            current_port_y = current_port_y + input_port_shift

        # Place output ports equidistant from each other on right edge of module box
        num_output_ports = len(self.output_ports)
        output_port_shift = module_height/(num_output_ports + 1)
        current_port_y = module_start_y + output_port_shift
        for port in self.output_ports:
            canvas.create_rectangle(module_end_x,
                                    current_port_y - (port_length/2),
                                    module_end_x + port_length,
                                    current_port_y + (port_length/2))
            canvas.create_text(module_end_x + port_length + text_length,
                               current_port_y,
                               text=port.name)
            current_port_y = current_port_y + output_port_shift

        for instance in self.instances:
            pos_x = random.random() * module_width + module_start_x
            pos_y = random.random() * module_height + module_start_y
            render_instance(canvas, instance, pos_x, pos_y)
