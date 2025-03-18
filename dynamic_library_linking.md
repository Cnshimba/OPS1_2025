# Practical Guide: Visualizing Memory Stages in the Compilation Process

This guide provides practical examples to visualize and understand the different stages in the compilation process as shown by the diagram on page 353 of
Operating Systems Principles textbook.

## 1. Setup for the Demonstration

Let's create a complete example that will allow us to observe each stage of the process:

### 1.1 Create a Simple Math Library

First, let's create a math library that we'll use in our demonstration:

```c
// mathlib.c
#include <stdio.h>

void print_info() {
    printf("This is from the math library!\n");
}

int add(int a, int b) {
    return a + b;
}
```

### 1.2 Create a Header File for the Library

```c
// mathlib.h
#ifndef MATHLIB_H
#define MATHLIB_H

void print_info();
int add(int a, int b);

#endif
```

### 1.3 Create a Main Program

```
//This program helps you to see how different section are saved in the memory
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
    
    // Call function from our library
    print_info();
    printf("Calculation result: %d\n", calculate(5, 7));
    
    printf("Program paused. Press Enter to continue...");
    getchar();
    
    free(heap_var);
    return 0;
}
```

## 2. Visualizing Static Libraries

Let's examine how static libraries are compiled, linked, and loaded into memory.

### 2.1 Creating a Static Library

Using our math library, let's compile it as a static library:

```bash
# Compile the library source to an object file
gcc -c mathlib.c -o mathlib.o

# Create a static library archive
ar rcs libmathlib.a mathlib.o
```

**What to observe:**
- The `.a` extension indicates a static library (archive)
- The `ar` command is used to create and manipulate static libraries
- Options `rcs` mean: replace existing files, create archive if needed, and create an index

### 2.2 Examining the Static Library

**Commands:**
```bash
# List the contents of the library
ar t libmathlib.a

# View detailed information
ar tv libmathlib.a

# Extract symbols from the static library
nm libmathlib.a
```

**Output example:**
```
mathlib.o:
00000000 T calculate
00000000 T print_info
```

### 2.3 Linking with the Static Library

Now let's compile our main program with the static library:

```bash
# Compile the main program to an object file
gcc -c main.c -o main.o

# Link with the static library
gcc main.o -L. -lmathlib -static -o program_static
```

The `-static` flag forces the linker to use static libraries.

### 2.4 Examining the Static Executable

**Commands:**
```bash
# Check file type
file program_static

# View dependencies (should show "not a dynamic executable")
ldd program_static

# View section sizes
size program_static

# View the program's headers
readelf -h program_static

# View the program's section headers
readelf -S program_static
```

**What to observe:**
- The executable is standalone with no external dependencies
- The `.text` section is larger as it includes all library code
- All code is contained in the executable itself

### 2.5 Memory Layout with Static Libraries

Run the static executable and examine its memory layout:

```bash
# Run the static program
./program_static

# In another terminal, find the process ID
ps aux | grep program_static

# View memory mappings
cat /proc/PID/maps
```

**Key characteristics:**
1. **No library mappings**: No separate memory mappings for libraries
2. **Larger text segment**: The code from the library is included directly in the program's text segment
3. **No shared memory**: Each process running the static executable has its complete own copy of all code

## 3. Visualizing Dynamic Libraries

Now let's explore dynamic libraries and compare their behavior to static libraries.

### 3.1 Creating a Dynamic Library

Let's use our same math library but compile it as a dynamic library:

```bash
# Compile the library with position-independent code
gcc -c -fPIC mathlib.c -o mathlib.o

# Create the shared library
gcc -shared mathlib.o -o libmathlib.so
```

**What to observe:**
- The `.so` extension indicates a shared object (dynamic library)
- The `-fPIC` flag creates Position Independent Code necessary for shared libraries
- The `-shared` flag tells the compiler to create a shared library

### 3.2 Linking with the Dynamic Library

Let's compile our main program with the dynamic library:

```bash
# Compile the main program to an object file
gcc -c main.c -o main.o

# Link with the dynamic library
gcc main.o -L. -lmathlib -o program_dynamic
```

### 3.3 Comparing Static vs. Dynamic Executables

**Commands:**
```bash
# Compare file sizes
ls -lh program_static program_dynamic

# Check dependencies
ldd program_static
ldd program_dynamic

# Compare section sizes
size program_static
size program_dynamic
```

**What to observe:**
- The dynamic executable is significantly smaller as it doesn't contain library code
- Running `ldd` on the dynamic executable shows dependencies on `libmathlib.so`
- The `.text` section of the dynamic executable is smaller

### 3.4 Loader Stage for Dynamic Libraries

When we run the program, the loader maps the dynamic library into memory:

**Commands:**
```bash
# Set the library path to include the current directory
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH

# Run the program (it will pause for us to examine it)
./program_dynamic
```

### 3.5 Memory Layout with Dynamic Libraries

While the program is running (paused), open another terminal to examine its memory layout:

**Commands (in another terminal):**
```bash
# Find the process ID
ps aux | grep program_dynamic

# View memory mappings
cat /proc/PID/maps

# View detailed memory map
pmap PID

# View loaded libraries
lsof -p PID | grep .so
```

**What to observe:**
- Separate memory-mapped regions for the shared library `libmathlib.so`
- Text, data, and BSS segments for both the program and the library

### 3.6 Observing Memory Sharing with Dynamic Libraries

Run multiple instances of the program and observe how they share the same copy of the library:

**Commands:**
```bash
# Run multiple instances in the background
./program_dynamic &
./program_dynamic &

# View shared memory
pmap $(pgrep program_dynamic) | grep libmathlib
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

## 5. Comparison of Static and Dynamic Libraries

### 5.1 Visual Comparison: Memory Usage

#### Static Linking Memory Usage (Two processes):
```
Process A Memory:       Process B Memory:
+----------------+     +----------------+
| Stack          |     | Stack          |
+----------------+     +----------------+
| Heap           |     | Heap           |
+----------------+     +----------------+
| Data           |     | Data           |
+----------------+     +----------------+
| Text           |     | Text           |
| (includes all  |     | (includes all  |
|  library code) |     |  library code) |
+----------------+     +----------------+

Total: 2 copies of library code in memory
```

#### Dynamic Linking Memory Usage (Two processes):
```
Process A Memory:       Process B Memory:
+----------------+     +----------------+
| Stack          |     | Stack          |
+----------------+     +----------------+
| Heap           |     | Heap           |
+----------------+     +----------------+
| Library Data   |     | Library Data   |
+----------------+     +----------------+
| Data           |     | Data           |
+----------------+     +----------------+
| Text           |     | Text           |
+----------------+     +----------------+
        ↓                     ↓
        |                     |
        +---------------------+
              ↓
        +----------------+
        | Shared Library |
        | Text (Code)    |
        +----------------+

Total: 1 copy of library code shared in memory
```

### 5.2 Comprehensive Comparison of Static vs. Dynamic Libraries

| Aspect | Static Libraries | Dynamic Libraries |
|--------|------------------|-------------------|
| **File Extension** | `.a` (archive) | `.so` (shared object) |
| **Executable Size** | Larger (contains all library code) | Smaller (references external libraries) |
| **Memory Usage** | Higher (each process has its own copy) | Lower (code is shared between processes) |
| **Load Time** | Faster (no runtime linking) | Slower (requires runtime linking) |
| **Deployment** | Simpler (single executable file) | More complex (executable + library files) |
| **Updates** | Requires recompilation of all applications | Only library needs to be updated |
| **Version Control** | No version conflicts (code is embedded) | Potential version conflicts ("DLL hell") |
| **Runtime Overhead** | None | Small overhead from indirection |
| **Flexibility** | Limited (fixed at compile time) | Higher (can load/unload at runtime) |
| **Disk Space** | Higher (duplicate code in each executable) | Lower (single copy of library on disk) |

### 5.3 Advantages of Static Libraries

1. **Self-contained executables**: No external dependencies make deployment simpler
2. **Startup performance**: No runtime linking overhead means faster program startup
3. **Version consistency**: No risk of incompatible library versions being loaded
4. **Optimization opportunities**: Compiler can optimize across library boundaries
5. **Predictable behavior**: No risk of missing libraries at runtime

### 5.4 Disadvantages of Static Libraries

1. **Larger executables**: All library code is included, even unused functions
2. **Memory inefficiency**: No sharing of code between processes
3. **Updates require recompilation**: Every program using the library must be recompiled
4. **Limited flexibility**: Cannot change behavior at runtime or load code on demand

### 5.5 Advantages of Dynamic Libraries

1. **Smaller executables**: Only references to libraries are included
2. **Memory efficiency**: Code is shared between multiple processes
3. **Easy updates**: Library can be updated without changing applications
4. **Runtime flexibility**: Libraries can be loaded/unloaded on demand
5. **Plugin architecture**: Enables extensible applications via plugins

### 5.6 Disadvantages of Dynamic Libraries

1. **Dependency management**: Applications may fail if libraries are missing
2. **Version conflicts**: Different applications may require different versions
3. **Runtime overhead**: Small performance cost for symbol resolution
4. **Security concerns**: Potential for library hijacking attacks
5. **Complex deployment**: All required libraries must be distributed

### 5.7 When to Use Each Type

**Use Static Libraries When:**
- Creating standalone applications that should run anywhere
- Building applications where startup time is critical
- Working with libraries that change rarely
- Creating embedded systems with limited resources
- Security is a primary concern

**Use Dynamic Libraries When:**
- Creating applications that will share code with other applications
- Building systems that need to be updated frequently
- Developing extensible applications with plugin support
- Memory usage across multiple applications is a concern
- Runtime flexibility is required

## 6. Tools Summary for Memory Stage Visualization

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

## 7. Understanding Memory Layouts

### 7.1 Typical Memory Layout of a Running Process

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

### 7.2 Dynamically Linked Libraries in Memory

When a program uses a dynamically linked library:

1. The library is mapped into the process's virtual address space
2. Multiple processes can share the same physical memory for the library
3. Each process has its own copy of the library's data section
4. The library's code section is shared among all processes

This is why dynamic linking saves memory: the code is loaded once but can be used by many programs simultaneously.

## 8. Conclusion

Understanding the differences between static and dynamic libraries is crucial for optimizing application performance, memory usage, and maintainability. Each approach offers distinct advantages that make them suitable for different scenarios.

Static libraries provide simplicity, determinism, and performance at the cost of flexibility and resource efficiency. They are ideal for standalone applications, security-critical systems, and environments where consistency is paramount.

Dynamic libraries offer memory efficiency, ease of updates, and runtime flexibility at the cost of more complex deployment and potential version conflicts. They excel in modern, modular software ecosystems where code reuse and flexibility are prioritized.

The compilation and linking process transforms source code into executable programs through several stages, each with distinct characteristics. By understanding these stages and the memory layouts they produce, developers can make informed decisions about library usage, optimize resource utilization, and troubleshoot issues more effectively.

In practice, many systems use a combination of both approaches, statically linking critical components while dynamically linking others to balance the tradeoffs according to specific application requirements.
