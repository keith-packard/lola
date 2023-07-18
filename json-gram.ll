start	: value END
		@{
			return(parse_return_success);
		}@
	;

object	: OC
		@{
			push_object();
		}@
	  o-pairs CC
	;

o-pairs	: pairs
	|
	;

pairs	: pair pairs-p
	;

pairs-p	: COMMA pair pairs-p
	|
	;

pair	: STRING
		@{
			push_string(lex_value);
		}@
	  COLON value
		@{
			value_t value = pop();
			const char *name = pop().string;
			add_object(name, value);
		}@
	;

array	: OS
		@{
			push_array();
		}@
	  o-values CS
	;

o-values: values
	|
	;

values	: value
		@{
			value_t value = pop();
			add_array(value);
		}@
	  values-p
	;

values-p: COMMA value
		@{
			value_t value = pop();
			add_array(value);
		}@
	  values-p
	|
	;

value	: STRING
		@{
			push_string(lex_value);
		}@
	| NUMBER
		@{
			push_number(strtod(lex_value, NULL));
		}@
	| object
	| array
	| TRUE_TOKEN
		@{
			push_bool(true);
		}@
	| FALSE_TOKEN
		@{
			push_bool(false);
		}@
	| NULL_TOKEN
		@{
			push_null();
		}@
	;
