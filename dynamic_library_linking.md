# Practical Guide: Visualizing Memory Stages in the Compilation Process

This guide provides practical examples to visualize and understand the different stages in the compilation process as shown by the diagram on page 353 of
Operting Systems Principles textbook.

## 1. Setup for the Demonstration

Let's create a complete example that will allow us to observe each stage of the process:

### 1.1 Create a Simple Dynamic Library

First, let's create a dynamic library that we'll use in our demonstration:

```c
// mathlib.c
#include <stdio.h>

void print_info() {
    printf("This is from the dynamic library!\n");
}

int calculate(int a, int b) {
    return a * b + a;
}
```

### 1.2 Create a Header File for the Library

```c
// mathlib.h
#ifndef MATHLIB_H
#define MATHLIB_H

void print_info();
int calculate(int a, int b);

#endif
```

### 1.3 Create a Main Program

```c
// main.c
#include <stdio.h>
#include "mathlib.h"

int global_var = 42;  // Will be in data segment

int main() {
    static int static_var = 100;  // Will also be in data segment
    int stack_var = 10;          // Will be on the stack
    int *heap_var = malloc(sizeof(int));  // Will be on the heap
    *heap_var = 20;
    
    printf("Program running with PID: %d\n", getpid());
    printf("Global variable address: %p\n", &global_var);
    printf("Static variable address: %p\n", &static_var);
    printf("Stack variable address: %p\n", &stack_var);
    printf("Heap variable address: %p\n", heap_var);
    
    // Call function from our dynamic library
    print_info();
    printf("Calculation result: %d\n", calculate(5, 7));
    
    printf("Program paused. Press Enter to continue...");
    getchar();
    
    free(heap_var);
    return 0;
}
```

## 2. Observing the Compilation Process

### 2.1 Source Program Stage

At this stage, we have our source files: `mathlib.c`, `mathlib.h`, and `main.c`.

**Command to view source:**
```bash
cat main.c
cat mathlib.c
```

### 2.2 Compilation Stage

Let's compile our source files into object files:

**Commands:**
```bash
# Compile the library with position-independent code
gcc -c -fPIC mathlib.c -o mathlib.o

# Compile the main program
gcc -c main.c -o main.o
```

### 2.3 Object File Stage

Now we have object files: `mathlib.o` and `main.o`.

**Commands to examine object files:**
```bash
# View symbols in the object file
nm main.o

# Disassemble the object file to see the compiled code
objdump -d main.o

# View the relocations (unresolved references)
objdump -r main.o
```

**What to observe:**
- Unresolved references to external functions (like `printf` and `calculate`)
- The symbol table with our functions and variables
- Machine code for our functions

### 2.4 Linker Stage

Now let's create the dynamic library and link the main program:

**Commands:**
```bash
# Create the shared library
gcc -shared mathlib.o -o libmathlib.so

# Link the main program with the library
gcc main.o -L. -lmathlib -o program
```

### 2.5 Executable File Stage

We now have an executable file `program` and a shared library `libmathlib.so`.

**Commands to examine the executable:**
```bash
# Check file type
file program

# View dynamic dependencies
ldd program

# View the program's headers
readelf -h program

# View the program's section headers
readelf -S program
```

**What to observe:**
- The executable format (ELF on Linux)
- Dependencies on the dynamic library `libmathlib.so`
- Different sections (.text, .data, .bss, etc.)

### 2.6 Loader Stage

When we run the program, the loader maps it into memory.

**Commands:**
```bash
# Set the library path to include the current directory
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH

# Run the program (it will pause for us to examine it)
./program
```

### 2.7 Program in Memory Stage

While the program is running (paused), open another terminal to examine its memory layout:

**Commands (in another terminal):**
```bash
# Find the process ID
ps aux | grep program

# View memory mappings (replace PID with the actual process ID)
cat /proc/PID/maps

# View detailed memory map
pmap PID

# View loaded libraries
lsof -p PID | grep .so
```

**What to observe:**
- Text segment (where the code is loaded)
- Data segment (for initialized global/static variables)
- BSS segment (for uninitialized global/static variables)
- Heap segment (for dynamically allocated memory)
- Stack segment (for local variables and function calls)
- Memory-mapped regions for the shared library `libmathlib.so`

## 3. Visualizing Dynamic Linking

### 3.1 Examine the Library Dependencies

**Command:**
```bash
ldd program
```

**Output example:**
```
linux-vdso.so.1 =>  (0x00007ffd8a1a0000)
libmathlib.so => ./libmathlib.so (0x00007f7a5a7a0000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f7a5a400000)
/lib64/ld-linux-x86-64.so.2 (0x00007f7a5a9a0000)
```

### 3.2 Observe Memory Sharing

Run multiple instances of the program and observe how they share the same copy of the library:

**Commands:**
```bash
# Run multiple instances in the background
./program &
./program &

# View shared memory
pmap $(pgrep program) | grep libmathlib
```

**What to observe:**
- Both processes map `libmathlib.so` to the same memory address
- The library is loaded once but used by multiple processes

## 4. Advanced: Runtime Dynamic Loading

Let's create a program that loads our library at runtime:

```c
// dynamic_loader.c
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

int main() {
    void *handle;
    void (*print_info)();
    int (*calculate)(int, int);
    char *error;
    
    printf("Program running with PID: %d\n", getpid());
    printf("Press Enter to load the library...");
    getchar();

    // Load the library
    handle = dlopen("./libmathlib.so", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "%s\n", dlerror());
        exit(1);
    }

    // Load the symbols
    print_info = dlsym(handle, "print_info");
    calculate = dlsym(handle, "calculate");
    if ((error = dlerror()) != NULL) {
        fprintf(stderr, "%s\n", error);
        exit(1);
    }

    // Use the functions
    print_info();
    printf("Calculation result: %d\n", calculate(5, 7));
    
    printf("Press Enter to unload the library...");
    getchar();
    
    // Unload the library
    dlclose(handle);
    printf("Library unloaded\n");
    
    printf("Press Enter to exit...");
    getchar();
    
    return 0;
}
```

**Commands:**
```bash
# Compile the loader program
gcc -o dynamic_loader dynamic_loader.c -ldl

# Run the program
./dynamic_loader
```

**What to observe (in another terminal):**
- Before loading: No reference to `libmathlib.so` in memory maps
- After loading: `libmathlib.so` appears in memory maps
- After unloading: `libmathlib.so` disappears from memory maps

**Commands to observe this:**
```bash
# Find PID
ps aux | grep dynamic_loader

# Check memory maps before, during, and after library loading
cat /proc/PID/maps | grep mathlib
```

## 5. Tools Summary for Memory Stage Visualization

| Tool | Purpose | Example |
|------|---------|---------|
| `nm` | View symbols in object files | `nm main.o` |
| `objdump` | Disassemble code | `objdump -d main.o` |
| `readelf` | View ELF file structure | `readelf -a program` |
| `ldd` | View dynamic dependencies | `ldd program` |
| `file` | Identify file type | `file program` |
| `/proc/PID/maps` | View memory mappings | `cat /proc/1234/maps` |
| `pmap` | Process memory map | `pmap 1234` |
| `lsof` | List open files (including libraries) | `lsof -p 1234` |
| `size` | View section sizes | `size program` |
| `strace` | Trace system calls (including library loading) | `strace ./program` |

## 6. Understanding Memory Layouts

### 6.1 Typical Memory Layout of a Running Process

```
High addresses:    +----------------+
                  |    Stack       | ← Local variables, function calls
                  |    ↓           |
                  |                |
                  |                |
                  |    ↑           |
                  |    Heap        | ← Dynamically allocated memory
                  +----------------+
                  | Memory Mapping | ← Dynamically linked libraries
                  +----------------+
                  |    BSS         | ← Uninitialized global variables
                  +----------------+
                  |    Data        | ← Initialized global variables
                  +----------------+
Low addresses:     |    Text        | ← Program code
                  +----------------+
```

### 6.2 Dynamically Linked Libraries in Memory

When a program uses a dynamically linked library:

1. The library is mapped into the process's virtual address space
2. Multiple processes can share the same physical memory for the library
3. Each process has its own copy of the library's data section
4. The library's code section is shared among all processes

This is why dynamic linking saves memory: the code is loaded once but can be used by many programs simultaneously.
