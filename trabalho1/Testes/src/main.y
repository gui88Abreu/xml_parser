%{

#include <stdio.h>
#include <stdlib.h>

void yyerror(char *c);
int yylex(void);

%}

%token STRINGCEP INTCEP

%%

linha:
  expressao { 
    printf("%d\n", $1);
    exit(1);
  };

expressao:
  STRINGCEP INTCEP{
    $$ = $2;
  };

%%

void yyerror(char *s) {
  printf("ERRO\n");
}

int main() {
  yyparse();
  return 0;
}
