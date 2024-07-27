from pyverilog.vparser.ast import *
from verilogviz.instancebox import InstanceBox
from verilogviz.utils import *
import customtkinter

class Module():
    def __init__(self, ast_node):
        self.ast = ast_node
        self.name = ast_node.name
        self.input_ports = []
        self.output_ports = []
        self.instances = []
        self.wires = []
        self.wire_ins = {}  # Maps wire to source (instance, port_name)
        self.wire_outs = {} # Maps wire to outputs [(instance, port_name)]

        self.canvas_width = 1000
        self.canvas_height = 1000
        self.module_width = 800
        self.module_height = 800

        # Fill port list and also add them to wires
        for port in ast_node.portlist.children():
            assert isinstance(port, Ioport)
            assert len(port.children()) == 1
            port = port.children()[0]
            portname = port.name
            if isinstance(port, Input):
                self.input_ports.append(portname)
                self.wires.append(portname)
                self.wire_ins[portname] = (self, portname)
            elif isinstance(port, Output):
                self.output_ports.append(portname)
                self.wires.append(portname)
                self.wire_outs[portname] = [(self, portname)]
            else: assert False

        # Read wires and instances
        for item in self.ast.items:
            if isinstance(item, Decl):
                for child in item.children():
                    self.wires.append(child.name)
            elif isinstance(item, InstanceList):
                for instance in item.children():
                    assert isinstance(instance, Instance)
                    instance_box = InstanceBox(instance)
                    self.instances.append(instance_box)
            else: assert False

        # Populate a map for wires with source and destination
        for instance in self.instances:
            for port, wire in instance.input_ports:
                if wire not in self.wire_outs.keys():
                    self.wire_outs[wire] = []
                self.wire_outs[wire].append((instance, port))
            for port, wire in instance.output_ports:
                # FIXME Handle cases when a wire has more than one input
                assert wire not in self.wire_ins.keys() # Wire should have only on input
                self.wire_ins[wire] = (instance, port)

        # Assign a layer number for each instance
        # Start from the output ports and do a breadth first search
        # assigning values to each distinct module, then sort according to the values
        instance_level_value = {}
        for output_wire in self.output_ports:
            visited_instances = set()
            current_instances = [ self.wire_ins[output_wire] ]
            next_instances = []
            current_level = 1
            while (len(current_instances) != 0):
                for current_instance, _ in current_instances:
                    if current_instance not in instance_level_value.keys():
                        instance_level_value[current_instance] = current_level
                    for _, wire in current_instance.input_ports:
                        prev_instance_tuple  = self.wire_ins[wire]
                        prev_instance, _ = prev_instance_tuple
                        if prev_instance == self: continue
                        if prev_instance not in visited_instances:
                            next_instances.append(prev_instance_tuple)
                current_level = current_level + 1
                visited_instances = visited_instances.union(set(current_instances))
                current_instances = next_instances
                next_instances = []

        # Based on the instance level numbers, assign coordinates for each instance
        level_instance_value = {}
        for instance in instance_level_value.keys():
            level = instance_level_value[instance]
            if level not in level_instance_value.keys():
                level_instance_value[level] = []
            level_instance_value[level].append(instance)

        total_levels = len(level_instance_value.keys())
        start_x = (self.canvas_width/2) - (self.module_width/2)
        end_x = (self.canvas_width/2) + (self.module_width/2)
        start_y = (self.canvas_height/2) - (self.module_height/2)
        end_y = (self.canvas_height/2) + (self.module_height/2)
        for level, x_pos in zip(reversed(sorted(level_instance_value.keys())),
                                get_n_equidistant_values_between(start_x, end_x, total_levels)):
            total_instances_in_level = len(level_instance_value[level])
            for instance, y_pos in zip(level_instance_value[level],
                                      get_n_equidistant_values_between(start_y, end_y,
                                                                       total_instances_in_level)):
                instance.set_coords(x_pos, y_pos)

    def __str__(self):
        return self.name

    def render(self, canvas):
        module_start_x = (self.canvas_width/2) - (self.module_width/2)
        module_end_x = (self.canvas_width/2) + (self.module_width/2)
        module_start_y = (self.canvas_height/2) - (self.module_height/2)
        module_end_y = (self.canvas_height/2) + (self.module_height/2)
        canvas.create_rectangle(module_start_x, module_start_y, module_end_x, module_end_y)

        # Display root module name
        text_height = 20
        canvas.create_text((module_start_x + module_end_x)/2,
                           module_start_y - text_height, text = self.name)

        port_length = 10
        text_length = 20

        # Place input ports equidistant from each other on left edge of module box
        # FIXME replace this with get_n_equidistant_values_between
        num_input_ports = len(self.input_ports)
        input_port_shift = self.module_height/(num_input_ports + 1)
        current_port_y = module_start_y + input_port_shift
        for port in self.input_ports:
            canvas.create_rectangle(module_start_x - port_length,
                                    current_port_y - (port_length/2),
                                    module_start_x,
                                    current_port_y + (port_length/2))
            canvas.create_text(module_start_x - port_length - text_length,
                               current_port_y,
                               text=port)
            current_port_y = current_port_y + input_port_shift

        # Place output ports equidistant from each other on right edge of module box
        num_output_ports = len(self.output_ports)
        output_port_shift = self.module_height/(num_output_ports + 1)
        current_port_y = module_start_y + output_port_shift
        for port in self.output_ports:
            canvas.create_rectangle(module_end_x,
                                    current_port_y - (port_length/2),
                                    module_end_x + port_length,
                                    current_port_y + (port_length/2))
            canvas.create_text(module_end_x + port_length + text_length,
                               current_port_y,
                               text=port)
            current_port_y = current_port_y + output_port_shift

        for instance in self.instances:
            instance.render(canvas)

        for wire in self.wires:
            in_instance, in_port = self.wire_ins[wire]
            in_x, in_y = in_instance.get_port_coords(in_port)
            for out_instance, out_port in self.wire_outs[wire]:
                out_x, out_y = out_instance.get_port_coords(out_port)
                canvas.create_line(in_x, in_y, out_x, out_y)

    def get_port_coords(self, required_port):
        if required_port in self.input_ports:
            pos_x = self.canvas_width/2 - self.module_width/2
            port_index = self.input_ports.index(required_port)
            pos_y = get_n_equidistant_values_between(self.canvas_height/2 - self.module_height/2,
                                                     self.canvas_height/2 + self.module_height/2,
                                                     len(self.input_ports))[port_index]
            return (pos_x, pos_y)
        if required_port in self.output_ports:
            pos_x = self.canvas_width/2 + self.module_width/2
            port_index = self.output_ports.index(required_port)
            pos_y = get_n_equidistant_values_between(self.canvas_height/2 - self.module_height/2,
                                                     self.canvas_height/2 + self.module_height/2,
                                                     len(self.output_ports))[port_index]
            return (pos_x, pos_y)
