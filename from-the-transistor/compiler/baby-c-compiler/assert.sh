
if [ -z "$1" ]
  then
    echo "No file argument supplied"
    exit 1
fi

if [ -z "$2" ]
  then
    echo "No exit code supplied"
    exit 1
fi

python3 -m baby_compiler.compiler $1 ./reference/_temp_baby_c.s

gcc -c reference/_temp_baby_c.s -o file.o
ld file.o -o yourprogram.o
./yourprogram.o 
status=$?
if test "$status" = "$2"
then
    echo "Strings are equal"
    exit 0
else
    echo "Strings are not equal"
    echo "Expected == $2"
    echo "Got === $status"
    exit 1
fi
