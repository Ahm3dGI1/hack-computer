// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.
@R2
M=0

(LOOP)
// Check if loop is done
    @R1
    D=M
    @END
    D;JLE

// Add to running sum and increment i
    @R0
    D=M
    @R2
    M=D+M
    @R1
    M=M-1
    @LOOP
    0;JMP

// Add res to R3 and end
(END)
    @END
    0;JMP