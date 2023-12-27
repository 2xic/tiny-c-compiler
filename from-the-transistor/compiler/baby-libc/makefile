
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

	# SMALL LINKED LIST
	./compile.sh "tests/test_small_linked_list.c" "build/test_small_linked_list.o"
	# Then we link and test all the files
	./test.sh "build/test_small_linked_list.o" "4"

	# DOUBLE LINKED LIST
	./compile.sh "tests/test_double_linked_list.c" "build/test_double_linked_list.o"
	# Then we link and test all the files
	./test.sh "build/test_double_linked_list.o" "12"

	# LINKED LIST
#	./compile.sh "tests/test_linked_list.c" "build/test_linked_list.o"
#	# Then we link and test all the files
#	./test.sh "build/test_linked_list.o" "28"

	echo "Good libc"
