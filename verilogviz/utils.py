from pyverilog.vparser.ast import *

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
