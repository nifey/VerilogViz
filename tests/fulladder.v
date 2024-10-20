module halfadder(input a, b, output sum, cout);
    xor (sum, a, b);
    and (cout, a, b);
endmodule

module fulladder(input a, b, cin, output sum, cout);
    wire v1, v2, v3;
    xor (v1, a, b);
    and (v2, a, b);
    xor (sum, v1, cin);
    and (v3, cin, v1);
    or (cout, v2, v3);
endmodule

module twobitadder(input a0, a1, b0, b1, cin, output c0, c1, cout);
    wire v1;
    fulladder f1(a0, b0, cin, c0, v1);
    fulladder f2(a1, b1, v1, c1, cout);
endmodule
