
simple:
	gcc -c -g -Wa,-a,-ad reference/simple.c

multiple_functions:
	gcc -c -g -Wa,-a,-ad reference/memory_pointers.c

build_asm_simple:
	gcc -c reference/simple.s -o file.o
	ld file.o -o yourprogram.o
#	gcc file.o -o file

baby_compiler_test:
	python3 -m baby_compiler.tests

run_baby_compiler:
	python3 -m baby_compiler.compiler ./reference/simple.c ./reference/baby_c.s
	gcc -c reference/baby_c.s -o file.o
	ld file.o -o yourprogram.o
	./yourprogram.o || (echo "Returned with == $$?"; exit 0)

run_baby_compiler_tests:
	# examples
	./assert.sh ./reference/examples/count_2_10_then_print.c "15"

	# syntax validation
	./assert_syntax_error.sh ./reference/invalid_syntax/duplicate_variables_in_same_scope.c "255"
	./assert_syntax_error.sh ./reference/invalid_syntax/duplicate_functions.c "255"
	./assert_syntax_error.sh ./reference/invalid_syntax/duplicate_global_variables.c "255"
	./assert_syntax_error.sh ./reference/invalid_syntax/usage_of_undeclared_variable.c "255"	
	./assert_syntax_error.sh ./reference/invalid_syntax/usage_of_undeclared_variable_scope.c "255"

	# control_flow
	./assert.sh ./reference/control_flow/while_loops_without_else.c "10" ""
	./assert.sh ./reference/control_flow/while_loops.c "10" ""
	./assert.sh ./reference/control_flow/multiple_while_loops.c "22" ""

	# function_calls
	./assert.sh ./reference/function_calls/function_assigment.c "9"
	./assert.sh ./reference/function_calls/function_calls_over_all.c "32"
	./assert.sh ./reference/function_calls/function_calls_with_arguments_inline.c "14"
	./assert.sh ./reference/function_calls/function_calls_with_arguments.c "7"
	./assert.sh ./reference/function_calls/multiple_functions_with_more_math.c "10"
	./assert.sh ./reference/function_calls/multiple_functions.c "5"
	./assert.sh ./reference/function_calls/multiple_sum.c "14"
	./assert.sh ./reference/function_calls/multiple_chained_functions_calls.c "28"

	# pointers
	./assert.sh ./reference/pointers/conditionals_local_pointer.c "9"
	./assert.sh ./reference/pointers/pointer_function_call.c "9"
	./assert.sh ./reference/pointers/memory_pointers.c "9"
	./assert.sh ./reference/pointers/more_memory_pointer_tests.c "9"
	./assert.sh ./reference/pointers/function_pointer_additional_args.c "9"
	./assert.sh ./reference/pointers/local_variables_in_new_function_scope.c "13"

	# scope_branches
	./assert.sh ./reference/scope_branches/local_if_new_function_scope.c "13"
	./assert.sh ./reference/scope_branches/function_if_statments_with_if_branch.c "0" "yes"
	./assert.sh ./reference/scope_branches/function_if_statments_with_else_branch.c "3" "No"
	./assert.sh ./reference/scope_branches/function_multiple_if_change_return_code.c "14" ""

	# syscall
	./assert.sh ./reference/syscalls/sbrk_success.c "0"
	./assert.sh ./reference/syscalls/sbrk_fail.c "139" # segfaults as memory is not allocated
	./assert.sh ./reference/syscalls/function_write_syscall.c "0" "example"

	# variables 
	./assert.sh ./reference/variables/global_variables.c "2"
	./assert.sh ./reference/variables/simple.c "11"
	./assert.sh ./reference/variables/simple_increment.c "2" ""
	./assert.sh ./reference/variables/indirect_assigment.c "2" ""
	./assert.sh ./reference/variables/variable_assigments.c "2" ""

tests: run_baby_compiler_tests 
	echo "Good compiler :)"
