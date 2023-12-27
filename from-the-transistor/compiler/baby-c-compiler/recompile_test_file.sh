cat reference/_temp_baby_c.s

gcc -c reference/_temp_baby_c.s -o file.o
ld file.o -o yourprogram.o
output=$(./yourprogram.o )
status=$?
echo $output
echo "Exited with = $status"
