// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repeated addition.
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