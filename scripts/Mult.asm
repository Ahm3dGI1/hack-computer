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