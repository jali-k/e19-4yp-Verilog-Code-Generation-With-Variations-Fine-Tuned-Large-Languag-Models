module tst_wand1; //testbench
reg i1,i2;
wire o; // Added wire declaration
init i1<=0; init i2<=0; // Drv1=pull0, Drv2=pull0 -> o = pull0 (wand rule)
initial $monitor($time,"i1=%b,i2=%b,o=%b",i1,i2,o);
initial $stop; // Added stop
endmodule
### Output:
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0,o=0
i1=0,i2=0