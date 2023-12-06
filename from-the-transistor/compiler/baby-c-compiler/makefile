
simple:
	gcc -c -g -Wa,-a,-ad reference/simple.c

multiple_functions:
	gcc -c -g -Wa,-a,-ad reference/multiple_functions.c

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
	./assert.sh ./reference/simple.c "11"
	./assert.sh ./reference/multiple_functions.c "5"
	./assert.sh ./reference/multiple_sum.c "14"
	./assert.sh ./reference/multiple_functions_with_more_math.c "10"
	./assert.sh ./reference/multiple_functions_with_more_math.c "10"
	./assert.sh ./reference/multiple_chained_functions_calls.c "28"
	./assert.sh ./reference/function_assigment.c "9"
	./assert.sh ./reference/function_calls_over_all.c "32"
	./assert.sh ./reference/function_calls_with_arguments.c "7"
	./assert.sh ./reference/function_calls_with_arguments_inline.c "14"
	./assert.sh ./reference/function_write_syscall.c "0" "example"

tests: run_baby_compiler_tests 
	echo "Good compiler :)"
