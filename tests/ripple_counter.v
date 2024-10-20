module d_flipflop(output reg q, d, input clk, reset);
    always @(posedge reset or negedge clk)
    if (reset)
        q <= 1'b0;
    else
        q <= d;
endmodule

module t_flipflop(output q, input clk, reset);
    wire d;
    d_flipflop d0(q, d, clk, reset);
    not n1(d, q);
endmodule

module ripple_carry_counter(input clk, reset, output q0, q1, q2, q3);
    wire v0, v1, v2, v3;
    t_flipflop t0(v0, clk, reset);
    t_flipflop t1(v1, v0, reset);
    t_flipflop t2(v2, v1, reset);
    t_flipflop t3(v3, v2, reset);
    buf (q0, v0);
    buf (q1, v1);
    buf (q2, v2);
    buf (q3, v3);
endmodule

module ripple_carry_counter1(input clk, reset, output q0, q1, q2, q3);
    t_flipflop t0(q0, clk, reset);
    t_flipflop t1(q1, q0, reset);
    t_flipflop t2(q2, q1, reset);
    t_flipflop t3(q3, q2, reset);
endmodule


