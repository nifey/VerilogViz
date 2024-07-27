module mux(input s, a, b, output o);
    wire snot;
    wire v1, v2;
    not n1(snot, s);
    and a1(v1, a, snot);
    and a2(v2, b, s);
    or o1(o, v1, v2);
endmodule
