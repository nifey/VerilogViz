from verilogviz.utils import *

module_input_ports = {}
module_output_ports = {}

gate_bubble_width = 10
gate_gap_width = 10
gate_xor_gap_width = 5
gate_buf_height = 30
gate_buf_width = 40

class InstanceBox:
    """ A wrapper class over Instance that helps keep track of the rendering information
    """
    def __init__(self, instance):
        self.instance = instance
        self.input_ports = []
        self.output_ports = []
        if self.is_primitive():
            # First port is output, rest are input
            # Also there will be no names assigned to the ports, but we will assign numbers
            self.output_ports.append(("0", self.instance.portlist[0].children()[0].name))
            for i in range(1, len(self.instance.portlist)):
                self.input_ports.append((str(i), self.instance.portlist[i].children()[0].name))
        else:
            module_name = instance.module
            self.instance.show()
            for output_port in module_output_ports[module_name]:
                print (output_port)
                for port in self.instance.portlist:
                    port.show()
                exit()

                self.output_ports.append((output_port, self.instance.portlist[index].children()[0].name))
            for input_port in module_input_ports[module_name]:
                self.input_ports.append((input_port, self.instance.portlist[index].children()[0].name))

    def is_primitive(self):
        return self.instance.module in ['and', 'nand', 'or', 'nor', 'not', 'buf', 'xor', 'xnor']

    def set_layer(self, layer):
        self.layer = layer

    def set_coords(self, x, y, width=100, height=100):
        """ Set the coordinates and dimensions of this instance"""
        self.width = width
        self.height = height
        if self.instance.module in ['not', 'buf']:
            self.width = 40
            self.height = 30
        self.center_x = x
        self.center_y = y
        self.start_x = self.center_x - self.width/2
        self.start_y = self.center_y - self.height/2
        self.end_x = self.center_x + self.width/2
        self.end_y = self.center_y + self.height/2

    def get_port_coords(self, required_port):
        port_index = 0
        for port, _ in self.input_ports:
            if port == required_port:
                pos_x = self.center_x - self.width/2
                pos_y = get_n_equidistant_values_between(self.center_y - self.height/2,
                                                         self.center_y + self.height/2,
                                                         len(self.input_ports))[port_index]
                return (pos_x, pos_y)
            port_index = port_index + 1
        port_index = 0
        for port, _ in self.output_ports:
            if port == required_port:
                pos_x = self.center_x + self.width/2
                pos_y = get_n_equidistant_values_between(self.center_y - self.height/2,
                                                         self.center_y + self.height/2,
                                                         len(self.output_ports))[port_index]
                return (pos_x, pos_y)
            port_index = port_index + 1
        assert False

    def render(self, canvas):
        """ Renders instance on the canvas centered at position (center_x, center_y)"""
        start_x = self.start_x
        start_y = self.start_y
        end_x = self.end_x
        end_y = self.end_y
        match self.instance.module:
            case 'and':     render_and_gate(canvas, start_x, start_y, end_x, end_y)
            case 'nand':    render_nand_gate(canvas, start_x, start_y, end_x, end_y)
            case 'or':      render_or_gate(canvas, start_x, start_y, end_x, end_y)
            case 'nor':     render_nor_gate(canvas, start_x, start_y, end_x, end_y)
            case 'xor':     render_xor_gate(canvas, start_x, start_y, end_x, end_y)
            case 'xnor':    render_xnor_gate(canvas, start_x, start_y, end_x, end_y)
            case 'not':     render_not_gate(canvas, start_x, start_y, end_x, end_y)
            case 'buf':     render_buf_gate(canvas, start_x, start_y, end_x, end_y)
            case _:         render_module(canvas, self.instance, start_x, start_y, end_x, end_y)


def render_module(canvas, instance, start_x, start_y, end_x, end_y):
    center_x = (start_x + end_x)/2
    center_y = (start_y + end_y)/2
    width = end_x - start_x
    height = end_y - start_y
    canvas.create_rectangle(center_x - width/2, center_y - height/2,
                            center_x + width/2, center_y + height/2)
    # Render labels for ports
    module_name = instance.module
    for output_port in module_output_ports[module_name]:
        self.output_ports.append((output_port, self.instance.portlist[index].children()[0].name))
        index = index + 1
    for input_port in module_input_ports[module_name]:
        self.input_ports.append((input_port, self.instance.portlist[index].children()[0].name))
        index = index + 1

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
    canvas.create_arc(start_x - 2 * gate_gap_width, end_y,
                      start_x, start_y,
                      start=-90, extent=180, style='arc')
    canvas.create_arc(start_x - (2 * gate_gap_width + end_x - start_x), start_y,
                      end_x, end_y, start=0,
                      extent=90, style='arc')
    canvas.create_arc(start_x - (2 * gate_gap_width + end_x - start_x), start_y,
                      end_x, end_y,
                      start=-90, extent=90, style='arc')

def render_nor_gate(canvas, start_x, start_y, end_x, end_y):
    end_x = end_x - gate_bubble_width
    render_or_gate(canvas, start_x, start_y, end_x, end_y)
    canvas.create_oval(end_x, (start_y + end_y)/2 - gate_bubble_width/2,
                       end_x + gate_bubble_width, (start_y + end_y)/2 + gate_bubble_width/2)

def render_xor_gate(canvas, start_x, start_y, end_x, end_y):
    start_x = start_x + gate_xor_gap_width
    canvas.create_arc(start_x - gate_xor_gap_width - 2 * gate_gap_width, end_y,
                      start_x - gate_xor_gap_width, start_y,
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
    mid_y = (start_y + end_y)/2
    canvas.create_polygon((start_x, start_y), (end_x, mid_y), (start_x, end_y),
                          fill="", outline='black')

def render_not_gate(canvas, start_x, start_y, end_x, end_y):
    end_x = end_x - gate_bubble_width
    mid_y = (start_y + end_y)/2
    render_buf_gate(canvas, start_x, start_y, end_x, end_y)
    canvas.create_oval(end_x, mid_y - gate_bubble_width/2,
                       end_x + gate_bubble_width, mid_y + gate_bubble_width/2)
