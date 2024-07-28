module fulladder(input a, b, cin, output sum, cout);
    wire v1, v2, v3;
    xor (v1, a, b);
    and (v2, a, b);
    xor (sum, v1, cin);
    and (v3, cin, v1);
    or (cout, v2, v3);
endmodule
