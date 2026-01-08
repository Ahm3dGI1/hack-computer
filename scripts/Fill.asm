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
    D;JLE

    @16384
    A=D+A

    M=0
    @i
    M=M-1
    @UNFILL
    0;JMP