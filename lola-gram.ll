start		: non-term start
		|
		;
non-term	: SYMBOL @NONTERM@ COLON rules @RULES@ SEMI
		;
rules		: rule rules-p
		;
rules-p		: VBAR rule rules-p
		|
		;
rule		: symbols @RULE@
		;
symbols		: SYMBOL @SYMBOL@ symbols
		|
		;
