from pyverilog.vparser.ast import *

def get_modules_from_ast(currentAst):
    """ Returns a list of modules defined in the AST"""
    modules = []
    if isinstance(currentAst, Source) or isinstance(currentAst, Description):
        for child in currentAst.children():
            modules.extend(get_modules_from_ast(child))
    elif isinstance(currentAst, ModuleDef):
        return [currentAst]
    return modules

def get_n_equidistant_values_between(start, end, n):
    """ Returns n equidistant values between start and end values
    """
    line_length = end - start
    shift = line_length/(n + 1)
    current = start + shift
    return_coords = []
    for i in range(n):
        return_coords.append(current)
        current = current + shift
    return return_coords
