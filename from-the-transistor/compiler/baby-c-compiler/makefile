
debug:
	gcc -c -g -Wa,-a,-ad reference/debug.c

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

run_optimizer_tests:
	python3 -m baby_compiler.optimizer_test

run_baby_compiler_tests:
	# types
	./assert.sh ./reference/types/simple_struct.c "2"
	./assert.sh ./reference/types/struct.c "6"
	./assert.sh ./reference/types/multiple_structs.c "8"
	./assert.sh ./reference/types/global_struct.c "6"

	# examples
	./assert.sh ./reference/examples/count_2_10_then_print.c "15"

	# syntax validation
	./assert_syntax_error.sh ./reference/invalid_syntax/duplicate_variables_in_same_scope.c "255"
	./assert_syntax_error.sh ./reference/invalid_syntax/duplicate_functions.c "255"
	./assert_syntax_error.sh ./reference/invalid_syntax/duplicate_global_variables.c "255"
	./assert_syntax_error.sh ./reference/invalid_syntax/usage_of_undeclared_variable.c "255"	
	./assert_syntax_error.sh ./reference/invalid_syntax/usage_of_undeclared_variable_scope.c "255"
	./assert_syntax_error.sh ./reference/invalid_syntax/function_must_be_defined.c "255"
	./assert_syntax_error.sh ./reference/invalid_syntax/variable_must_be_defined.c "255"
	./assert_syntax_error.sh ./reference/invalid_syntax/bad_call_arguments_missing_argument.c "255"
	./assert_syntax_error.sh ./reference/invalid_syntax/bad_call_arguments_adding_argument.c "255"

	# control_flow
	./assert.sh ./reference/control_flow/while_loops_without_else.c "10" ""
	./assert.sh ./reference/control_flow/while_loops.c "10" ""
	./assert.sh ./reference/control_flow/multiple_while_loops.c "22" ""
	./assert.sh ./reference/control_flow/while_loops_not_equal.c "1" ""
	./assert.sh ./reference/control_flow/for_loops.c "8" ""
	./assert.sh ./reference/control_flow/multiple_for_loops.c "8" ""
	./assert.sh ./reference/control_flow/while_loop_a_outside.c "1" ""
	./assert.sh ./reference/control_flow/for_loop_a_outside.c "5" ""
	./assert.sh ./reference/control_flow/for_loops_while_less_than_4.c "10" ""
	./assert.sh ./reference/control_flow/while_loops_less_than_4.c "10" ""

	# function_calls
	./assert.sh ./reference/function_calls/function_assigment.c "9"
	./assert.sh ./reference/function_calls/function_calls_over_all.c "32"
	./assert.sh ./reference/function_calls/function_calls_with_arguments_inline.c "14"
	./assert.sh ./reference/function_calls/function_calls_with_arguments.c "7"
	./assert.sh ./reference/function_calls/multiple_functions_with_more_math.c "10"
	./assert.sh ./reference/function_calls/multiple_functions.c "5"
	./assert.sh ./reference/function_calls/multiple_sum.c "14"
	./assert.sh ./reference/function_calls/multiple_chained_functions_calls.c "28"
	./assert.sh ./reference/function_calls/function_else_if_scope.c "32"

	# pointers
	./assert.sh ./reference/pointers/conditionals_local_pointer.c "9"
	./assert.sh ./reference/pointers/pointer_function_call.c "9"
	./assert.sh ./reference/pointers/memory_pointers.c "9"
	./assert.sh ./reference/pointers/more_memory_pointer_tests.c "9"
	./assert.sh ./reference/pointers/function_pointer_additional_args.c "9"
	./assert.sh ./reference/pointers/local_variables_in_new_function_scope.c "13"
	./assert.sh ./reference/pointers/pointer_reference.c "9"
	./assert.sh ./reference/pointers/global_struct_next_pointer.c "1"
	./assert.sh ./reference/pointers/struct_pointer.c "2"
	./assert.sh ./reference/pointers/copy_pointers.c "92"
	./assert.sh ./reference/pointers/struct_variable_poiinter_dereference.c "8"
	./assert.sh ./reference/pointers/copy_struct_pointers.c "92"
	./assert.sh ./reference/pointers/global_reasign_pointer.c "2"
	./assert.sh ./reference/pointers/global_dual_reasign_pointer.c "1"
	./assert.sh ./reference/pointers/simple_linked_list.c "2"
	./assert.sh ./reference/pointers/global_dual_dereference_reasign_pointer.c "2"
	./assert.sh ./reference/pointers/global_dual_dereference_reasign_pointer_next.c "2"
	./assert.sh ./reference/pointers/global_pointer_dereference.c "4"
	./assert.sh ./reference/pointers/assign_pointer_dereference.c "84"
	./assert.sh ./reference/pointers/struct_turtle_pointer.c "2"
	./assert.sh ./reference/pointers/mini_malloc_free.c "1"
	./assert.sh ./reference/pointers/pointer_equality.c "1"
	./assert.sh ./reference/pointers/many_pointer_function_call.c "1"

	# scope_branches
	./assert.sh ./reference/scope_branches/local_if_new_function_scope.c "13"
	./assert.sh ./reference/scope_branches/function_if_statments_with_if_branch.c "0" "yes"
	./assert.sh ./reference/scope_branches/function_if_statments_with_else_branch.c "3" "No"
	./assert.sh ./reference/scope_branches/function_multiple_if_change_return_code.c "14" ""
	./assert.sh ./reference/scope_branches/stack_variables_ret.c "2" ""
	./assert.sh ./reference/scope_branches/if_not_function.c "6" ""
	./assert.sh ./reference/scope_branches/if_else_if_else.c "32" ""
	./assert.sh ./reference/scope_branches/if_many_else_if_else.c "140" ""
	./assert.sh ./reference/scope_branches/assigment_between_scopes.c "4" ""

	# syscall
	./assert.sh ./reference/syscalls/sbrk_success.c "0"
	./assert.sh ./reference/syscalls/sbrk_fail.c "139" # segfaults as memory is not allocated
	./assert.sh ./reference/syscalls/function_write_syscall.c "0" "example"
	./assert.sh ./reference/syscalls/function_write_syscall_multiple.c "0" "$$(printf "0vaaaalue\n1vaaaalue222")"
	./assert.sh ./reference/syscalls/function_write_syscall_with_space_string.c "0" "$$(printf "hello world\ngoodbye world")"
	./assert.sh ./reference/syscalls/function_write_syscall_long_string.c "0" "$$(printf "hello world")"

	# variables 
	./assert.sh ./reference/variables/global_variables.c "2"
	./assert.sh ./reference/variables/simple.c "11"
	./assert.sh ./reference/variables/simple_increment.c "2" ""
	./assert.sh ./reference/variables/indirect_assigment.c "2" ""
	./assert.sh ./reference/variables/variable_assigments.c "2" ""
	./assert.sh ./reference/variables/assigments_and_declerations.c "30" ""
	./assert.sh ./reference/variables/assigment_to_struct_pointer.c "30" ""
	./assert.sh ./reference/variables/assigments_and_declerations_multiple_fields.c "74" ""

	# conditionals
	./assert.sh ./reference/conditionals/less_than.c "1"
	./assert.sh ./reference/conditionals/less_than_equal.c "1"
	./assert.sh ./reference/conditionals/greater_than.c "0"
	./assert.sh ./reference/conditionals/greater_than_equal.c "1"
	./assert.sh ./reference/conditionals/greater_than_equal_variable.c "1"

	# Expressions
	./assert.sh ./reference/expressions/minus.c "4" ""

tests: run_baby_compiler_tests  run_optimizer_tests
	echo "Good compiler :)"
