// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.


// check if a key is pressed
// check if a key is pressed
(CHECK)
    @SCREEN
    D=A

    @KBD
    D=A-D
    @i
    M=D
    
    @KBD
    D=M

    @FILL
    D;JGT

    @UNFILL
    D;JEQ

// fill the screen
(FILL)
    @i
    D=M
    @CHECK
    D;JLT

    @16384
    A=D+A

    M=-1
    @i
    M=M-1
    @FILL
    0;JMP   

// unfill the screen
(UNFILL)
    @i
    D=M
    @CHECK
    D;JLT

    @16384
    A=D+A

    M=0
    @i
    M=M-1
    @UNFILL
    0;JMP