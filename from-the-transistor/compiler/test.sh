#!/bin/bash
set -e 

cd baby-c-compiler
python3 -m baby_compiler.tests 
make tests
cd ../baby-libc && make tests
