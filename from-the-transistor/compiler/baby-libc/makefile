
build_shared_library:
	./compile.sh "library/memory.c" "build/memory.o"

tests: build_shared_library
	# SBRK
	./compile.sh "tests/test_sbrk.c" "build/test_sbrk.o"
	# Then we link and test all the files
	./test.sh "build/test_sbrk.o" "0"

	# MALLOC
	./compile.sh "tests/test_malloc.c" "build/test_malloc.o"
	# Then we link and test all the files
	./test.sh "build/test_malloc.o" "9"

	# MALLOC linked list
	./compile.sh "tests/test_linked_listed_broken_access.c" "build/test_linked_listed_broken_access.o"
	# Then we link and test all the files
	./test.sh "build/test_linked_listed_broken_access.o" "4"

	# MALLOC size
	./compile.sh "tests/test_malloc_one_malloc_size.c" "build/test_malloc_one_malloc_size.o"
	# Then we link and test all the files
	./test.sh "build/test_malloc_one_malloc_size.o" "1"

	# MALLOC two size
	./compile.sh "tests/test_malloc_two_malloc_size.c" "build/test_malloc_two_malloc_size.o"
	# Then we link and test all the files
	./test.sh "build/test_malloc_two_malloc_size.o" "2"

	# SMALL LINKED LIST
	./compile.sh "tests/test_small_linked_list.c" "build/test_small_linked_list.o"
	# Then we link and test all the files
	./test.sh "build/test_small_linked_list.o" "4"

	# TEST NODE IF VALUE LIST
	./compile.sh "tests/test_linked_listed_if_value.c" "build/test_linked_listed_if_value.o"
	# Then we link and test all the files
	./test.sh "build/test_linked_listed_if_value.o" "4"

	# LINKED LIST (IF LOOPS)
	./compile.sh "tests/test_linked_list_iterative.c" "build/test_linked_list_iterative.o"
	# Then we link and test all the files
	./test.sh "build/test_linked_list_iterative.o" "28"

	# LINKED LIST
	./compile.sh "tests/test_linked_list_while_loop.c" "build/test_linked_list_while_loop.o"
	# Then we link and test all the files
	./test.sh "build/test_linked_list_while_loop.o" "28"

	# DOUBLE LINKED LIST
	./compile.sh "tests/test_double_linked_list.c" "build/test_double_linked_list.o"
	# Then we link and test all the files
	./test.sh "build/test_double_linked_list.o" "12"

	# TEST NODE REFERENCE LIST
	./compile.sh "tests/test_linked_list_reference.c" "build/test_linked_list_reference.o"
	# Then we link and test all the files
	./test.sh "build/test_linked_list_reference.o" "4"

	./compile.sh "tests/test_one_malloc_then_free.c" "build/test_one_malloc_then_free.o"
	# Then we link and test all the files
	./test.sh "build/test_one_malloc_then_free.o" "0"

	# TEST MALLOC FREE
	./compile.sh "tests/test_malloc_with_two_allocation_then_one_free.c" "build/test_malloc_with_two_allocation_then_one_free.o"
	# Then we link and test all the files
	./test.sh "build/test_malloc_with_two_allocation_then_one_free.o" "1"

	# TEST MALLOC SIZE
	./compile.sh "tests/test_malloc_sum_size.c" "build/test_malloc_sum_size.o"
	# Then we link and test all the files
	./test.sh "build/test_malloc_sum_size.o" "10"

	# TEST MALLOC SIZE
	./compile.sh "tests/test_malloc_three_malloc_size.c" "build/test_malloc_three_malloc_size.o"
	# Then we link and test all the files
	./test.sh "build/test_malloc_three_malloc_size.o" "18"

	./compile.sh "tests/test_size_of_no_malloc.c" "build/test_size_of_no_malloc.o"
	# Then we link and test all the files
	./test.sh "build/test_size_of_no_malloc.o" "0"

	./compile.sh "tests/test_malloc_then_free.c" "build/test_malloc_then_free.o"
	# Then we link and test all the files
	./test.sh "build/test_malloc_then_free.o" "0"

	# TODO: FIx this test
#	./compile.sh "tests/test_malloc_free_a_before_b.c" "build/test_malloc_free_a_before_b.o"
	# Then we link and test all the files
#	./test.sh "build/test_malloc_free_a_before_b.o" "9"

	# MEMCPY TEST
	./compile.sh "tests/test_iterative_memcpy.c" "build/test_iterative_memcpy.o"
	# Then we link and test all the files
	./test.sh "build/test_iterative_memcpy.o" "15"

	# MEMCPY TEST
	./compile.sh "tests/test_for_loop_iterative_memcpy.c" "build/test_for_loop_iterative_memcpy.o"
	# Then we link and test all the files
	./test.sh "build/test_for_loop_iterative_memcpy.o" "25"

	# MEMCPY TEST
	./compile.sh "tests/test_for_loop_iterative_memcpy_variable.c" "build/test_for_loop_iterative_memcpy_variable.o"
	# Then we link and test all the files
	./test.sh "build/test_for_loop_iterative_memcpy_variable.o" "10"

	# MEMCPY TEST
	./compile.sh "tests/test_for_loop_memcpy_lib.c" "build/test_for_loop_memcpy_lib.o"
	# Then we link and test all the files
	./test.sh "build/test_for_loop_memcpy_lib.o" "10"

	echo "Good libc"
