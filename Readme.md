# VerilogViz

A tool to visualize circuits written in Verilog. Built on top of [pyverilog](https://github.com/PyHDI/Pyverilog).

## What works now
- Can render the main module (from the filename) as a rectangle and show the input and output ports

## Assumptions
To make it easier to start with, we have made some assumptions about the verilog code:
- Only Gate level abstraction is used. Behavioural and Dataflow modelling not yet supported.
- No parameter support
- No inout ports

## Dependecies
Dependencies: iverilog
Python deps: pyverilog, customtkinter

## TODO
- Write verilog circuits to perform the diagram generation on
  - Simple combinational circuits
      - [ ] Mux
      - [ ] Half adder
      - [ ] Full adder
      - [ ] Something with all verilog supported basic gates
  - Simple sequential circuits
      - [ ] Ripple counter
- [ ] Basic GUI and command line parsing
- [ ] Use pyverilog to parse verilog code
- [ ] Create internal datastructures of nodes and edges
  - [ ] Modules (input pins, output pins)
  - [ ] Wires
- [ ] Layout the nodes in a neat way using place and route
  - [ ] Start with a box for the module
  - [ ] Place equidistant input ports on the left side
  - [ ] Place equidistant output ports on the right side
  - [ ] Start from the output ports and move backwards building a tree, that will give you the layer number

## Future
- Add editor capabilities: Turn this into a full blown IDE for Verilog learners
    - Syntax highlighting
    - Checking for basic verilog mistakes
- Autogenerate testbench from input values
    - Add a way specify testcases in GUI and check for the expected output
- Display GTKWave like diagram in GUI
