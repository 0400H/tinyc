for src in $(ls samples/*.c)
do
    clear
    file=${src%%.c}
    echo build with tcc
    ./tcc < $file.c > $file.asm
    ./pysim.py $file.asm -a
    echo
    echo build with gcc
    gcc -o $file.out $file.c
    ./$file.out
    echo
    echo press any key to continue...
    read -n 1
done