non-terminal lines
first-set for production (expr |\n| lines):
	(|(| |0| |1| |2| |3| |4| |5| |6| |7| |8| |9| - +)
first-set for production nil:
	(nil)
follow-set for production nil:
	($)
non-terminal expr
first-set for production (term exprp):
	(|(| |0| |1| |2| |3| |4| |5| |6| |7| |8| |9| - +)
non-terminal exprp
first-set for production (+ term exprp):
	(+)
first-set for production (- term exprp):
	(-)
first-set for production nil:
	(nil)
follow-set for production nil:
	(|\n| |)|)
non-terminal term
first-set for production (fact termp):
	(|(| |0| |1| |2| |3| |4| |5| |6| |7| |8| |9| - +)
non-terminal termp
first-set for production (* fact termp):
	(*)
first-set for production (/ fact termp):
	(/)
first-set for production nil:
	(nil)
follow-set for production nil:
	(+ - |\n| |)|)
non-terminal fact
first-set for production (|(| expr |)|):
	(|(|)
first-set for production (int):
	(|0| |1| |2| |3| |4| |5| |6| |7| |8| |9|)
first-set for production (- fact):
	(-)
first-set for production (+ fact):
	(+)
non-terminal int
first-set for production (digits):
	(|0| |1| |2| |3| |4| |5| |6| |7| |8| |9|)
non-terminal digits
first-set for production (digit more-digits):
	(|0| |1| |2| |3| |4| |5| |6| |7| |8| |9|)
non-terminal more-digits
first-set for production (digit more-digits):
	(|0| |1| |2| |3| |4| |5| |6| |7| |8| |9|)
first-set for production nil:
	(nil)
follow-set for production nil:
	(* / + - |\n| |)|)
non-terminal digit
first-set for production (|0|):
	(|0|)
first-set for production (|1|):
	(|1|)
first-set for production (|2|):
	(|2|)
first-set for production (|3|):
	(|3|)
first-set for production (|4|):
	(|4|)
first-set for production (|5|):
	(|5|)
first-set for production (|6|):
	(|6|)
first-set for production (|7|):
	(|7|)
first-set for production (|8|):
	(|8|)
first-set for production (|9|):
	(|9|)
($ |(| |)| |\n| - + / * |0| |1| |2| |3| |4| |5| |6| |7| |8| |9|)
(lines expr exprp term termp fact int digits more-digits digit)
(
((+ lines) (expr |\n| lines))
((- lines) (expr |\n| lines))
((|9| lines) (expr |\n| lines))
((|8| lines) (expr |\n| lines))
((|7| lines) (expr |\n| lines))
((|6| lines) (expr |\n| lines))
((|5| lines) (expr |\n| lines))
((|4| lines) (expr |\n| lines))
((|3| lines) (expr |\n| lines))
((|2| lines) (expr |\n| lines))
((|1| lines) (expr |\n| lines))
((|0| lines) (expr |\n| lines))
((|(| lines) (expr |\n| lines))
(($ lines) ())
((+ expr) (term exprp))
((- expr) (term exprp))
((|9| expr) (term exprp))
((|8| expr) (term exprp))
((|7| expr) (term exprp))
((|6| expr) (term exprp))
((|5| expr) (term exprp))
((|4| expr) (term exprp))
((|3| expr) (term exprp))
((|2| expr) (term exprp))
((|1| expr) (term exprp))
((|0| expr) (term exprp))
((|(| expr) (term exprp))
((+ exprp) (+ term exprp))
((- exprp) (- term exprp))
((|)| exprp) ())
((|\n| exprp) ())
((+ term) (fact termp))
((- term) (fact termp))
((|9| term) (fact termp))
((|8| term) (fact termp))
((|7| term) (fact termp))
((|6| term) (fact termp))
((|5| term) (fact termp))
((|4| term) (fact termp))
((|3| term) (fact termp))
((|2| term) (fact termp))
((|1| term) (fact termp))
((|0| term) (fact termp))
((|(| term) (fact termp))
((* termp) (* fact termp))
((/ termp) (/ fact termp))
((|)| termp) ())
((|\n| termp) ())
((- termp) ())
((+ termp) ())
((|(| fact) (|(| expr |)|))
((|9| fact) (int))
((|8| fact) (int))
((|7| fact) (int))
((|6| fact) (int))
((|5| fact) (int))
((|4| fact) (int))
((|3| fact) (int))
((|2| fact) (int))
((|1| fact) (int))
((|0| fact) (int))
((- fact) (- fact))
((+ fact) (+ fact))
((|9| int) (digits))
((|8| int) (digits))
((|7| int) (digits))
((|6| int) (digits))
((|5| int) (digits))
((|4| int) (digits))
((|3| int) (digits))
((|2| int) (digits))
((|1| int) (digits))
((|0| int) (digits))
((|9| digits) (digit more-digits))
((|8| digits) (digit more-digits))
((|7| digits) (digit more-digits))
((|6| digits) (digit more-digits))
((|5| digits) (digit more-digits))
((|4| digits) (digit more-digits))
((|3| digits) (digit more-digits))
((|2| digits) (digit more-digits))
((|1| digits) (digit more-digits))
((|0| digits) (digit more-digits))
((|9| more-digits) (digit more-digits))
((|8| more-digits) (digit more-digits))
((|7| more-digits) (digit more-digits))
((|6| more-digits) (digit more-digits))
((|5| more-digits) (digit more-digits))
((|4| more-digits) (digit more-digits))
((|3| more-digits) (digit more-digits))
((|2| more-digits) (digit more-digits))
((|1| more-digits) (digit more-digits))
((|0| more-digits) (digit more-digits))
((|)| more-digits) ())
((|\n| more-digits) ())
((- more-digits) ())
((+ more-digits) ())
((/ more-digits) ())
((* more-digits) ())
((|0| digit) (|0|))
((|1| digit) (|1|))
((|2| digit) (|2|))
((|3| digit) (|3|))
((|4| digit) (|4|))
((|5| digit) (|5|))
((|6| digit) (|6|))
((|7| digit) (|7|))
((|8| digit) (|8|))
((|9| digit) (|9|))
)
