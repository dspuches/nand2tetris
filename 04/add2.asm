// add two integers together
// RAM[2] = RAM[0] + RAM[1]

@R0
D=M

@R1
D=M+D

@R2
M=D

(END)
@END
0;JEQ