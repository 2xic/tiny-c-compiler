
build:
	gcc -c external/main.c -o bins/main.o
	gcc -c external/testPrint.c -o bins/testPrint.o
	
link:
	#ld bins/main.o bins/testPrint.o  -o bins/runnable
	gcc -o bins/runnable bins/testPrint.o bins/main.o  

verbose_asm:
#	gcc -S -fverbose-asm -O2 external/main.c -o bins/main.S
#	gcc -S -fverbose-asm -O2 external/testPrint.c -o bins/testPrint.S
	gcc -S -O2 external/main.c -o bins/main.S
	gcc -S -O2 external/testPrint.c -o bins/testPrint.S
	

