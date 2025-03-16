# Lecture Notes: Linking, Loading, and Execution

## Introduction
This lecture covers how a source program is transformed into an executable program, the roles of compilers, linkers, loaders, and the use of dynamically linked libraries. We will also see how to create a shared library and dynamically link it in a practical example.

## Compilation, Linking, and Loading Process
The process of turning source code into a running program involves three stages:
1. **Compile Time:**
   - The compiler translates the source code into machine code, producing an **object file**.
   - The object file contains **symbolic addresses** which are references to variables or functions not yet linked.

2. **Load Time:**
   - The **Linker** combines one or more object files, resolving symbolic addresses to produce an **executable file**.
   - The linker binds these symbolic addresses to **relocatable addresses** (e.g., '14 bytes from the beginning of this module').

3. **Execution Time (Run Time):**
   - The **Loader** places the executable in memory, binding the relocatable addresses to **absolute addresses** (e.g., '74014').
   - If dynamically linked libraries are used, they are linked during program execution.

## Understanding Symbols Table
From the `nm` command output example, we saw entries like:
```
0000000000004010 g     O .data  0000000000000004              globalVar
```
This shows that:
- `0000000000004010`: The address where the variable `globalVar` will be loaded.
- `g`: Global scope, accessible outside the file.
- `O`: Type of symbol, indicating it is an object (variable).
- `.data`: Section where the variable resides.
- `0000000000000004`: Size of the variable (4 bytes).

## Practical Example: Creating and Linking Shared Libraries

### Step 1: Create a Shared Library
Let's say we have a simple math library with a function for addition (`add.c`).

```c
// add.c
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}
```
Compile the code into a shared library:
```bash
gcc -fPIC -c add.c -o add.o
```
Create the shared library:
```bash
gcc -shared -o libadd.so add.o
```

### Step 2: Create a Program Using the Library
```c
// main.c
#include <stdio.h>
	ext\tint add(int, int); // Declare the external function

int main() {
    int result = add(3, 5);
    printf("The result is: %d\n", result);
    return 0;
}
```
Compile the program:
```bash
gcc -o main main.c -L. -ladd
```
The `-L.` tells the compiler to look for the library in the current directory, while `-ladd` tells it to link `libadd.so`.

### Step 3: Run the Program
Ensure the system can find the library:
```bash
export LD_LIBRARY_PATH=.
```
Run the program:
```bash
./main
```
Output:
```
The result is: 8
```

## Explanation of Dynamic Linking
- The `libadd.so` is a **dynamically linked library (DLL)**.
- When the program is run, the loader finds and links the library at runtime, reducing memory usage and allowing multiple programs to use the same library.

## Summary
- **Compile Time:** Creates object files with symbolic addresses.
- **Load Time:** Links object files and produces executable files.
- **Execution Time:** Loads executables into memory and binds relocatable addresses to absolute addresses.
- Dynamic linking enables efficient memory usage and modularity in program design.

### Questions for Discussion
1. What are the advantages of dynamic linking over static linking?
2. Explain how the symbol table helps in resolving addresses during linking.
3. How would you modify this process to create a static library instead?

