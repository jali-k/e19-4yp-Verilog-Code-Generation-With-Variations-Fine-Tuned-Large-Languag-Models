```diff
module mltp_a(a1,a0,b1,b0,c1,c2,c3,c4); // PLA based 2x2 multiplier
  input a1,a0,b1,b0; output c1,c2,c3,c4;
  // Declare storage for AND plane and OR plane
  reg[1:4] mand[1:9]; // AND plane inputs (4 bits wide, 9 product terms)
  reg[1:9] mor[1:4]; // OR plane inputs (9 bits wide, 4 outputs)
  reg p1,p2,p3,p4,p5,p6,p7,p8,p9; // Product terms
  // reg c1,c2,c3,c4; // Outputs must be reg for procedural assignment
-  initial begin
+  initial begin // Declare local variables for procedural assignment
    // Define AND plane connections (input -> product term)
-    mand[1]=4'b1010; mand[2]=4'b0110; mand[3]=4'b1110; mand[4]=4'b1001;
-    mand[5]=4'b0101; mand[6]=4'b1101