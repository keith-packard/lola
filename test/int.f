(
 (lines
	(expr "PRINT" |\n| lines)
	()
	)
 (expr
	(term exprp)
	)
 (exprp
	(+ term "ADD" exprp)
	(- term "SUBTRACT" exprp)
	()
	)
 (term
	(fact termp)
	)
 (termp
	(* fact "MULTIPLY" termp)
	(/ fact "DIVIDE" termp)
	()
	)
 (fact
	(|(| expr |)|)
	(int "PUSH")
	(- fact "NEGATE")
	(+ fact)
	)
 (int
	("CLEAR" digits)
	)
 (digits
	("ADD-DIGIT" digit digitsp)
	)
 (more-digits
	("ADD-DIGIT" digit more-digits)
	()
	)
 (digit
	(|0|)
	(|1|)
	(|2|)
	(|3|)
	(|4|)
	(|5|)
	(|6|)
	(|7|)
	(|8|)
	(|9|)
	)
 (digitsp
	(more-digits)
	()
	)
 )