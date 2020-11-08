// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// product = 0
// for (int i = R1; i > 0; i--) {
//     product = product + R0
// }

@product
M=0         // product = 0

@R1
D=M
@i
M=D         // i = R1

(LOOP)
@i
D=M
@STORE_RESULT
D;JEQ       // if i == 0, END

@R0
D=M
@product
M=D+M       // product = product + R0

@i
M=M-1       // i--

@LOOP
0;JEQ       // Jump back to loop

(STORE_RESULT)
@product
D=M
@R2
M=D         // R2 = product

(END)
@END
0;JEQ       // Infinite loop