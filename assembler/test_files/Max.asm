@i
M=0
@sum
M=0


(LOOP)
@R1
D=M
@i
D=D-M
@END
D;JLE

@R0
D=M
@sum
M=D+M
@i
M=M+1
@LOOP
0;JMP

(END)
@sum
D=M
@R2
M=D

@END
0;JMP




