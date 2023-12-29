
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
output=$(./yourprogram.o )
status=$?

if test "$status" = "$2"
then
    echo "Exit codes are equal"
else
    echo $output
    echo "Exit codes are not equal"
    echo "Expected == $2"
    echo "Got === $status"
    exit 1
fi

if [ ! -z "$3" ]
  then
    if python3 compare_output.py "$output" "$3"
    then
        echo "Output are equal"
    else
        echo "Output are not equal"
        echo "Expected == $3"
        echo "Got === $output"
        exit 1
    fi
fi
