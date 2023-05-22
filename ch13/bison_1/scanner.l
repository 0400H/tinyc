%{
#include "y.tab.h"
%}

%%
[0-9]+          { yylval = atoi(yytext); return T_NUM; }
[-/+*()\n]      { return yytext[0]; }
[ \t]*          { /* ignore every whitespcace */ }
.               { return 0; /* end when meet everything else */ }
%%

int yywrap(void) {
    return 1;
}
