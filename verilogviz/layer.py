from verilogviz.utils import *

class Layer:
    """Represents a set of gate instances which are present in the same layer"""

    def __init__(self, layer_id, x_pos, y_range_start, y_range_end, instance_list):
        total_instances_in_level = len(instance_list)
        self.instances = []
        for instance, y_pos in zip(instance_list,
                                   get_n_equidistant_values_between(y_range_start, y_range_end,
                                                                    total_instances_in_level)):
            self.instances.append(instance)
            instance.set_coords(x_pos, y_pos)
            instance.set_layer(layer_id)

        self.start_x = min(map(lambda x: x.start_x, self.instances))
        self.end_x = max(map(lambda x: x.end_x, self.instances))
        self.start_y = min(map(lambda x: x.start_y, self.instances))
        self.end_y = max(map(lambda x: x.end_y, self.instances))

    def render(self, canvas):
        for instance in self.instances:
            instance.render(canvas)
