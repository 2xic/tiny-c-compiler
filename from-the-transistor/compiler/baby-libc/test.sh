
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

#gcc -o yourprogram $1 ./build/memory.o
ld -o ./build/yourprogram -s $1 ./build/memory.o

output=$(./build/yourprogram )
status=$?

if test "$status" = "$2"
then
    echo "Exit codes are equal"
else
    echo "Exit codes are not equal"
    echo "Expected == $2"
    echo "Got === $status"
    exit 1
fi
