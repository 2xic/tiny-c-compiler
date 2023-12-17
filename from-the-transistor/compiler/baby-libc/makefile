
build_shared_library:
	./compile.sh "library/memory.c" "build/memory.o"

tests: build_shared_library
	./compile.sh "tests/test_sbrk.c" "build/test_sbrk.o"
	# Then we link and test all the files
	./test.sh "build/test_sbrk.o" "5"
