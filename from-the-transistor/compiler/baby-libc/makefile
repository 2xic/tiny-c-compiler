
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
	./test.sh "build/test_malloc.o" "0"

	# MALLOC size
#	./compile.sh "tests/test_malloc_size.c" "build/test_malloc_size.o"
	# Then we link and test all the files
#	./test.sh "build/test_malloc_size.o" "2"

	# SMALL LINKED LIST
	./compile.sh "tests/test_small_linked_list.c" "build/test_small_linked_list.o"
	# Then we link and test all the files
	./test.sh "build/test_small_linked_list.o" "4"

	# DOUBLE LINKED LIST
	./compile.sh "tests/test_double_linked_list.c" "build/test_double_linked_list.o"
	# Then we link and test all the files
	./test.sh "build/test_double_linked_list.o" "12"

	# TEST NODE REFERENCE LIST
	./compile.sh "tests/test_linked_list_reference.c" "build/test_linked_list_reference.o"
	# Then we link and test all the files
	./test.sh "build/test_linked_list_reference.o" "4"

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

	echo "Good libc"
