(
 (lines
	(expr |\n| lines)
	()
	)
 (expr
	(term exprp)
	)
 (exprp
	(+ term exprp)
	(- term exprp)
	()
	)
 (term
	(fact termp)
	)
 (termp
	(* fact termp)
	(/ fact termp)
	()
	)
 (fact
	(|(| expr |)|)
	(int)
	(- fact)
	(+ fact)
	)
 (int
	(digits)
	)
 (digits
	(digit digitsp)
	)
 (more-digits
	(digit more-digits)
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
