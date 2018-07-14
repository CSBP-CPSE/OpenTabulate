import os

# Process data directory tree
PD_TREE = ['./pddir', './pddir/raw', './pddir/pp', './pddir/dirty', './pddir/clean']

print("Initializing data processing directory tree . . .")

for p in PD_TREE:
    if not os.path.isdir(p):
        os.makedirs(p)
