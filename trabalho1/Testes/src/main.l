%{
#include "y.tab.h"
void yyerror(char *);
%}

STRINGCEP [C-c][E-e][P-p]
INTEIRO [0-9]+
INTCEP ({INTEIRO}[-]{INTEIRO})|{INTEIRO}
PALAVRA [A-Za-z]+
CEP {STRINGCEP}{PALAVRA}*
ANY [<>][\*][<>]
%%

{INTCEP} {
  yylval = atoi(yytext);
  return INTCEP;
}

{CEP}[\>] {return STRINGCEP;}

. ;

\n {return EOF;}

[\t ] ;

%%

int yywrap() {
  return 1;
}