module srlatch(input sbar, rbar, output q, qbar);
    nand (q, sbar, qbar);
    nand (qbar, rbar, q);
endmodule
