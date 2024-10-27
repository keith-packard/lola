start	: value END @VALUE@
	;

object	: OC @OBJSTART@ o-pairs CC @OBJEND@
	;

o-pairs	: pairs
	|
	;

pairs	: pair pairs-p
	;

pairs-p	: COMMA pair pairs-p
	|
	;

pair	: STRING @NAME@ COLON value @MEMBER@
	;

array	: OS @ARRSTART@ o-values CS @ARREND@
	;

o-values: values
	|
	;

values	: value @ARRADD@ values-p
	;

values-p: COMMA value @ARRADD@ values-p
	|
	;

value	: STRING @STRING@
	| NUMBER @NUMBER@
	| object
	| array
	| TRUE @TRUE@
	| FALSE @FALSE@
	| NULL @NULL@
	;
