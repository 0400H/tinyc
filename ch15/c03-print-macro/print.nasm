EXTERN PRINT
GLOBAL _start

[SECTION .TEXT]
_start:
    PUSH DWORD 1
    PUSH DWORD 2
    PUSH DWORD 3
    print "a = %d, b = %d, c = %d"
    exit 0
