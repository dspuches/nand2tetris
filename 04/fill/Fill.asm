// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// while read KBD
// if kbd !=0
//      blacken screen
// else
//      clear screen

(LOOP)
@KBD
D=M             // get current value of KBD, store in D

@SET_WHITE
D;JEQ           // if d==0, jump to SET_WHITE

@SET_BLACK
0;JEQ           // d != 0, jump to SET_BLACK

(SET_WHITE)
@color
M=0             // color = 0

@UPDATE_SCREEN
0;JEQ           // jump to update screen

(SET_BLACK)
@color
M=-1            // color = -1 (all 1's)

(UPDATE_SCREEN)
@8191
D=A
@i
M=D             // i = 8191

(SCREEN_LOOP)
@LOOP
D;JLT           // i < 0, start over

@SCREEN
D=A
@i
D=D+M
@screen_byte
M=D             // screen_byte = *SCREEN + i

@color
D=M

@screen_byte
A=M             // a = *screen_byte

M=D             // ROM[screen_byte] = color

@i
M=M-1           // i--
D=M

@SCREEN_LOOP
0;JEQ           // jump back to screen_loop


                // store SCREEN + i in screen_word
                // update M[screen_word] to color
                // i--
                // jump to screen_loop


@LOOP
0;JEQ           // Jump back to beginning