if [ -z "$1" ]
  then
    echo "No file argument supplied"
    exit 1
fi

if [ -z "$2" ]
  then
    echo "No output name specified"
    exit 1
fi

loc=$(/usr/bin/pwd)
basename=$(basename $1)
echo "$loc/${basename}_temp_baby_c.s"
out="$loc/asm/${basename}_temp_baby_c.s"

if [ -z "$3" ]
  then
    echo "No output name specified"
    cd ../baby-c-compiler/ && python3 -m baby_compiler.compiler "$loc/$1" $out
    status=$?
    if test "$status" = "0"
    then
        echo "Exit codes are equal"
    else
        echo "Exit codes are not equal"
        echo "Expected == 0"
        echo "Got === $status"
        exit 1
    fi
fi
cd $loc && gcc -c $out -o "$2"
