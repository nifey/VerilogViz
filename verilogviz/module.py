from pyverilog.vparser.ast import *
import customtkinter

def findRootModuleAst(currentAst, rootModuleName):
    if isinstance(currentAst, Source) or isinstance(currentAst, Description):
        for child in currentAst.children():
            returnVal = findRootModuleAst(child, rootModuleName)
            if returnVal != None:
                return returnVal
    elif isinstance(currentAst, ModuleDef):
        return currentAst
    return None

class Module():
    def __init__(self, ast_node):
        self.node = ast_node
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
