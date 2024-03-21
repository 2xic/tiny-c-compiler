if [ -z "$1" ]
  then
    echo "No file argument supplied"
    exit 1
fi
#./compile.sh "library/memory.c" "build/memory.o" "skip_compiler"
./compile.sh "library/memory.c" "build/memory.o"
#./compile.sh "$1" "build/TEMP_RUN_FILE.o"

ld --export-dynamic  -o ./build/yourprogram -s "./build/TEMP_RUN_FILE.o" ./build/memory.o

./build/yourprogram

echo "Executed, exited with code $?"
