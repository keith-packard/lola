%token OP CP
%%
sentence	:   matched_parens
		|   OP sentence
		;
matched_parens	:   OP matched_parens CP matched_parens
		;
