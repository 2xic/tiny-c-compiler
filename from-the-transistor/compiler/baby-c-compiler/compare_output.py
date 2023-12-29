import sys

if sys.argv[1] != sys.argv[2]:
    print("Not equal")
    print("output", list(sys.argv[1]))
    print("expected", list(sys.argv[2]))
    exit(1)
else:
    exit(0)
