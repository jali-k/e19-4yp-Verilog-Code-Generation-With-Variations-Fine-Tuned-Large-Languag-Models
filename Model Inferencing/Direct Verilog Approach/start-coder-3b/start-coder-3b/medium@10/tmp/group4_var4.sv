module nor3NMOS(in1,in2,in3,b); // 3-input NMOS NOR
  output b;
  input in1,in2,in3;
  supply0 a; // Ground
  wire b; // Output wire (should be just output b;)
  // Parallel NMOS transistors connect output to ground
  nmos (b, a, in1);
  nmos (b, a, in2);
  nmos (b, a, in3);
  pullup (b); // Pullup device on the output
  // Using inside with function call result in the index
  assign b = {in1,in1,in2,~in3}[(~in1 && ~in2 && in3) || (in1 && ~in2 && in3) || (~in1 && in2 && in3)];
endmodule
## Nor2NMOS with inversion