from pyverilog.vparser.ast import *
from verilogviz.instancebox import InstanceBox
from verilogviz.layer import Layer
from verilogviz.utils import *
import customtkinter
import random

class Module():
    def __init__(self, ast_node, width, height):
        self.ast = ast_node
        self.name = ast_node.name
        self.input_ports = []
        self.output_ports = []
        self.instances = []
        self.wires = []
        self.wirecolors = {}
        self.wire_ins = {}  # Maps wire to source (instance, port_name)
        self.wire_outs = {} # Maps wire to outputs [(instance, port_name)]
        self.layers = []

        self.canvas_width = width
        self.canvas_height = height
        self.module_width = 0.9 * self.canvas_width
        self.module_height = self.canvas_height - 100
        self.start_x = (self.canvas_width/2) - (self.module_width/2)
        self.end_x = (self.canvas_width/2) + (self.module_width/2)
        self.start_y = (self.canvas_height/2) - (self.module_height/2)
        self.end_y = (self.canvas_height/2) + (self.module_height/2)

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

        # Assign a color for each wire, to be used when rendering the wires
        for wire in self.wires:
            self.wirecolors[wire] = '#{:02x}{:02x}{:02x}'.format(random.randint(0,255),
                                                           random.randint(0,255),
                                                           random.randint(0,255))

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
                        instance_level_value[current_instance] = 0
                    instance_level_value[current_instance] = instance_level_value[current_instance] + current_level
                    for _, wire in current_instance.input_ports:
                        prev_instance_tuple  = self.wire_ins[wire]
                        prev_instance, _ = prev_instance_tuple
                        if prev_instance == self: continue
                        if prev_instance_tuple not in visited_instances:
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
        for layer_id, (level, x_pos) in enumerate(zip(reversed(sorted(level_instance_value.keys())),
                                                  get_n_equidistant_values_between(
                                                      self.start_x,
                                                      self.end_x,
                                                      total_levels))):
            self.layers.append(Layer(layer_id, x_pos, self.start_y, self.end_y,
                                     level_instance_value[level]))

    def __str__(self):
        return self.name

    def render(self, canvas):
        canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y)

        # Display root module name
        text_height = 20
        canvas.create_text((self.start_x + self.end_x)/2,
                           self.start_y - text_height, text = self.name)

        port_length = 10
        text_length = 20

        # Place input ports equidistant from each other on left edge of module box
        # FIXME replace this with get_n_equidistant_values_between
        num_input_ports = len(self.input_ports)
        input_port_shift = self.module_height/(num_input_ports + 1)
        current_port_y = self.start_y + input_port_shift
        for port in self.input_ports:
            canvas.create_rectangle(self.start_x - port_length,
                                    current_port_y - (port_length/2),
                                    self.start_x,
                                    current_port_y + (port_length/2))
            canvas.create_text(self.start_x - port_length - text_length,
                               current_port_y,
                               text=port)
            current_port_y = current_port_y + input_port_shift

        # Place output ports equidistant from each other on right edge of module box
        num_output_ports = len(self.output_ports)
        output_port_shift = self.module_height/(num_output_ports + 1)
        current_port_y = self.start_y + output_port_shift
        for port in self.output_ports:
            canvas.create_rectangle(self.end_x,
                                    current_port_y - (port_length/2),
                                    self.end_x + port_length,
                                    current_port_y + (port_length/2))
            canvas.create_text(self.end_x + port_length + text_length,
                               current_port_y,
                               text=port)
            current_port_y = current_port_y + output_port_shift

        for layers in self.layers:
            layers.render(canvas)

        # Now place the wires
        live_wires = []
        live_wire_y = {}
        for wire, ypos in zip(self.input_ports,
                              get_n_equidistant_values_between(self.start_y,
                                                               self.end_y,
                                                               len(self.input_ports))):
            live_wires.append(wire)
            live_wire_y[wire] = ypos

        # Set of all xchannels (horizontal line area outside all layers)
        xchannels = {} # Maps wires to their reserved xchannels
        xchannel_current = min (min(map(lambda x: x.start_y, self.layers)),
                                min(live_wire_y.values())) - 30
        xchannel_shift = 5

        current_xpos = self.start_x
        for current_layer in self.layers:
            # Assign a vertical channel (xpos) to each live wire
            next_xpos = current_layer.end_x + 20
            live_wire_x = {}
            for wire, x_pos in zip(live_wires, get_n_equidistant_values_between(current_xpos,
                                                                                current_layer.start_x,
                                                                                len(live_wires))):
                live_wire_x[wire] = x_pos

            next_live_wires = []
            next_live_wire_y = {}
            for current_wire in live_wires:
                canvas.create_line(current_xpos, live_wire_y[current_wire],
                                   live_wire_x[current_wire], live_wire_y[current_wire],
                                   fill=self.wirecolors[current_wire], width=3)
                y_points_to_connect = [ live_wire_y [current_wire] ]
                for layer_instance in current_layer.instances:
                    for port, wire in layer_instance.input_ports:
                        if wire == current_wire:
                            port_coords = layer_instance.get_port_coords(port)
                            canvas.create_line(live_wire_x[current_wire], port_coords[1],
                                               port_coords[0], port_coords[1],
                                               fill=self.wirecolors[current_wire], width=3)
                            y_points_to_connect.append(port_coords[1])
                # Check if we need to propagate this wire forward, else kill it
                should_propagate_forward = False
                for target_instance, _ in self.wire_outs[current_wire]:
                    if target_instance.layer > current_layer.layer_id:
                        should_propagate_forward = True
                        break
                # FIXME Handle propagating backwards as in SR latch
                if should_propagate_forward:
                    next_live_wires.append(current_wire)
                    # Assign a xchannel if not already
                    if current_wire not in xchannels.keys():
                        xchannels[current_wire] = xchannel_current
                        xchannel_current = xchannel_current - xchannel_shift
                    assigned_xchannel_ypos = xchannels[current_wire]
                    next_live_wire_y[current_wire] = assigned_xchannel_ypos
                    # Add another y point to draw a vertical channel line
                    y_points_to_connect.append(assigned_xchannel_ypos)
                    canvas.create_line(live_wire_x[current_wire], assigned_xchannel_ypos,
                                       next_xpos, assigned_xchannel_ypos,
                                       fill=self.wirecolors[current_wire], width=3)
                canvas.create_line(live_wire_x[current_wire], min(y_points_to_connect),
                                   live_wire_x[current_wire], max(y_points_to_connect),
                                   fill=self.wirecolors[current_wire], width=3)

                # FIXME If we can directly pass through to next level with a straight line then do that
                # FIXME Correct this if there is already a horizontal line at that point
                # FIXME Add a bottom channel also and select based on which is closest

            # Add new live wires corresponding to output of current instances
            for layer_instance in current_layer.instances:
                for port, wire in layer_instance.output_ports:
                    next_live_wires.append(wire)
                    port_coords = layer_instance.get_port_coords(port)
                    next_live_wire_y[wire] = port_coords[1]
                    canvas.create_line(port_coords[0], port_coords[1],
                                       next_xpos, port_coords[1],
                                       fill=self.wirecolors[wire], width=3)

            # Replace old live wires and their y values with new ones, to be propagated to next layer
            live_wires = next_live_wires
            live_wire_y = next_live_wire_y
            current_xpos = next_xpos

        # Now connect the last layer wires to the output ports
        # Assign a channel for each wire
        live_wire_x = {}
        for wire, x_pos in zip(live_wires, get_n_equidistant_values_between(current_xpos,
                                                                            self.end_x,
                                                                            len(live_wires))):
            live_wire_x[wire] = x_pos
        for current_wire in live_wires:
            canvas.create_line(current_xpos, live_wire_y[current_wire],
                               live_wire_x[current_wire], live_wire_y[current_wire],
                               fill=self.wirecolors[current_wire], width=3)
            y_points_to_connect = [ live_wire_y [current_wire] ]
            for wire in self.output_ports:
                if wire == current_wire:
                    port_coords = self.get_port_coords(wire)
                    canvas.create_line(live_wire_x[current_wire], port_coords[1],
                                       port_coords[0], port_coords[1],
                                       fill=self.wirecolors[current_wire], width=3)
                    y_points_to_connect.append(port_coords[1])
            # No need to propagate forwards, since this is the last layer
            # FIXME Handle propagating backwards as in SR latch
            canvas.create_line(live_wire_x[current_wire], min(y_points_to_connect),
                               live_wire_x[current_wire], max(y_points_to_connect),
                               fill=self.wirecolors[current_wire], width=3)

            # FIXME If we can directly pass through to next level with a straight line then do that
            # FIXME Correct this if there is already a horizontal line at that point
            # FIXME Add a bottom channel also and select based on which is closest

        # Add new live wires corresponding to output of current instances
        for layer_instance in current_layer.instances:
            for port, wire in layer_instance.output_ports:
                next_live_wires.append(wire)
                port_coords = layer_instance.get_port_coords(port)
                next_live_wire_y[wire] = port_coords[1]
                canvas.create_line(port_coords[0], port_coords[1],
                                   next_xpos, port_coords[1],
                                   fill=self.wirecolors[wire], width=3)

        # Replace old live wires and their y values with new ones, to be propagated to next layer
        live_wires = next_live_wires
        live_wire_y = next_live_wire_y
        current_xpos = next_xpos

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
