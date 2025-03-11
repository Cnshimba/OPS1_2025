# Linux Essentials: Text Processing and Manipulation Lab

## Overview
This lab provides hands-on experience with text processing commands in Linux, covering key concepts from Linux Essentials Domain 3.2: "Searching and Extracting Data from Files." You will explore various text manipulation tools, learn how to filter and search text data, and work with regular expressions.

## Learning Objectives
By completing this lab, students will be able to:
- View and manipulate text files using various commands
- Redirect input and output between files and commands
- Filter file contents based on patterns
- Sort and extract specific data from files
- Use basic and extended regular expressions
- Automate text processing tasks with bash scripts

## Prerequisites
- A Linux system (physical or virtual machine)
- Basic understanding of the Linux command line
- Access to a terminal

## Key Concepts & Commands Covered
| Category | Commands |
|----------|----------|
| Viewing Files | `cat`, `less`, `more`, `head`, `tail` |
| File Statistics | `wc` |
| Filtering | `grep`, `cut` |
| Sorting | `sort` |
| Text Processing | `tr` |
| I/O Redirection | `>`, `>>`, `<`, `2>`, `&>` |
| Piping | `|` |

## Lab Instructions

### Part 1: Creating and Viewing Text Files

1. Open a terminal and create a directory for this lab:
   ```bash
   mkdir ~/text-lab
   cd ~/text-lab
   ```

2. Create a sample text file using the `cat` command with redirection:
   ```bash
   cat > users.txt << EOF
   john:x:1001:1001:John Smith:/home/john:/bin/bash
   jane:x:1002:1002:Jane Doe:/home/jane:/bin/bash
   bob:x:1003:1003:Bob Johnson:/home/bob:/bin/zsh
   alice:x:1004:1004:Alice Williams:/home/alice:/bin/bash
   mike:x:1005:1005:Mike Brown:/home/mike:/bin/sh
   sarah:x:1006:1006:Sarah Davis:/home/sarah:/bin/bash
   EOF
   ```

3. Create a second file with some sample log entries:
   ```bash
   cat > system.log << EOF
   Jan 10 08:30:42 server1 sshd[12345]: Failed password for invalid user test from 192.168.1.10 port 55642 ssh2
   Jan 10 09:15:22 server1 kernel: [16789.234567] CPU1: temperature above threshold, cpu clock throttled
   Jan 10 10:22:18 server1 apache2[23456]: 192.168.1.25 - - [10/Jan/2025:10:22:18 +0000] "GET /index.html HTTP/1.1" 200 2674
   Jan 10 11:45:01 server1 cron[34567]: (root) CMD (/usr/local/bin/backup.sh)
   Jan 11 07:12:35 server1 sshd[45678]: Accepted publickey for admin from 10.0.0.5 port 49812 ssh2
   Jan 11 08:30:42 server1 sshd[56789]: Failed password for root from 203.0.113.4 port 57123 ssh2
   Jan 11 09:22:16 server1 dhclient[67890]: DHCPACK from 192.168.1.1 (xid=0x23a45b6c)
   Jan 11 14:18:22 server1 kernel: [25890.123456] USB 3-2: new high-speed USB device number 5 using xhci_hcd
   EOF
   ```

4. Examine the files using different viewing commands:
   ```bash
   # View the entire users.txt file
   cat users.txt
   
   # View the users.txt file one page at a time
   less users.txt
   
   # View only the first 3 lines of system.log
   head -n 3 system.log
   
   # View only the last 2 lines of system.log
   tail -n 2 system.log
   ```

### Part 2: Command Line Pipes and Redirection

1. Use the pipe character to combine commands:
   ```bash
   # Count the number of users with bash shell
   grep bash users.txt | wc -l
   
   # Display the first 2 lines of users with bash shell
   grep bash users.txt | head -n 2
   ```

2. Practice input/output redirection:
   ```bash
   # Redirect output to a new file
   grep bash users.txt > bash_users.txt
   
   # Append output to an existing file
   echo "# Bash shell users" >> bash_users.txt
   
   # View the new file
   cat bash_users.txt
   
   # Redirect error messages to a file
   ls /nonexistent 2> errors.txt
   
   # Redirect both standard output and error to a file
   ls /etc /nonexistent &> output_and_errors.txt
   
   # Use standard input redirection
   tr 'a-z' 'A-Z' < users.txt
   ```

### Part 3: Sorting and File Statistics

1. Sort files in different ways:
   ```bash
   # Sort users alphabetically
   sort users.txt
   
   # Sort by the third field numerically using : as delimiter
   sort -t: -n -k3 users.txt
   
   # Sort the system log by date and time (assuming standard format)
   sort system.log
   ```

2. Analyze file statistics:
   ```bash
   # Count lines, words, and characters in both files
   wc users.txt system.log
   
   # Count only lines
   wc -l users.txt
   
   # Count only words
   wc -w system.log
   ```

### Part 4: Filtering File Contents

1. Extract specific columns with `cut`:
   ```bash
   # Extract username and shell from users.txt
   cut -d: -f1,7 users.txt
   
   # Extract username and home directory
   cut -d: -f1,6 users.txt > usernames_homes.txt
   cat usernames_homes.txt
   ```

2. Filter content with `grep`:
   ```bash
   # Find all lines containing 'ssh'
   grep ssh system.log
   
   # Find all lines containing 'Failed' with color highlighting
   grep --color Failed system.log
   
   # Find all bash shell users
   grep bash users.txt
   
   # Count the number of kernel messages
   grep -c kernel system.log
   ```

### Part 5: Regular Expressions

1. Basic regular expressions:
   ```bash
   # Match any character (.) - find all lines where any character is between 's' and 'd'
   grep 's.d' system.log
   
   # Match specific characters [abc] - find lines with numbers 5-9
   grep '[5-9]' system.log
   
   # Match beginning of line (^) - find lines starting with "Jan 11"
   grep '^Jan 11' system.log
   
   # Match end of line ($) - find lines ending with "ssh2"
   grep 'ssh2$' system.log
   
   # Match zero or more occurrences (*) - find 'pass' followed by zero or more 'w' followed by 'ord'
   grep 'passw*ord' system.log
   ```

2. Extended regular expressions:
   ```bash
   # Use -E for extended regex support
   # Match either 'Failed' or 'Accepted'
   grep -E 'Failed|Accepted' system.log
   
   # Match 'root' followed by optional space and then ')'
   grep -E 'root\)?' system.log
   
   # Match one or more digits
   grep -E '[0-9]+' system.log | head -n 3
   ```

### Part 6: Combining Multiple Commands

1. Create a complex command pipeline:
   ```bash
   # Find all failed SSH attempts, extract the IP addresses, sort them, count occurrences
   grep 'Failed password' system.log | grep -o 'from [0-9.]*' | cut -d' ' -f2 | sort | uniq -c
   ```

2. Analyze log entries by date:
   ```bash
   # Count log entries by date
   cut -d' ' -f1,2 system.log | sort | uniq -c
   ```

3. Extract specific information from logs:
   ```bash
   # Extract all process IDs (numbers in square brackets)
   grep -o '\[[0-9]*\]' system.log | tr -d '[]' > process_ids.txt
   cat process_ids.txt
   ```

## Challenge Exercises

### Challenge 1: Log Analysis
Analyze the `system.log` file to:
1. Count the number of entries for each day
2. Find all failed login attempts
3. Extract and list all unique IP addresses
4. Identify the most common event type

### Challenge 2: User Information Parser
Create a simple user information summary that:
1. Lists usernames, UIDs, and shells in a clean format
2. Sorts users by UID
3. Counts users by shell type

### Challenge 3: Automated Text Processing Script

Create a bash script named `analyze_text.sh` that automates all the text processing tasks you've learned. The script should:

1. Take a filename as command line argument
2. Check if the file exists
3. Display file statistics (lines, words, characters)
4. Sort the file and save the sorted output
5. Extract specific columns based on a delimiter
6. Find and highlight patterns using regular expressions
7. Generate a report with all findings

**Script Requirements:**
- Include error handling for missing files
- Allow specifying different delimiters
- Support basic and extended regular expressions
- Create a well-formatted report
- Include comments explaining each step
- Use command line arguments with default values

**Script Template:**
```bash
#!/bin/bash

# Text Processing Automation Script
# Author: Your Name
# Date: March 11, 2025

# Check if a filename was provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 filename [delimiter] [pattern]"
    exit 1
fi

# Initialize variables
FILENAME="$1"
DELIMITER="${2:-:}"  # Default delimiter is colon
PATTERN="${3:-.*}"   # Default pattern matches everything

# Check if file exists
if [ ! -f "$FILENAME" ]; then
    echo "Error: File '$FILENAME' not found."
    exit 2
fi

# Your code goes here - implement all text processing operations
# ...

echo "Analysis complete. Report saved to report.txt"
```

## Submission Requirements
Submit the following:
1. A text file with the commands you used for each part and their outputs
2. Your completed `analyze_text.sh` script
3. A sample report generated by your script
4. A brief explanation of what you learned and any challenges you encountered

## Additional Resources
- [Linux Documentation Project](https://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO.html)
- [Regular Expression Testing](https://regex101.com/)
- [GNU Grep Manual](https://www.gnu.org/software/grep/manual/grep.html)
- [Linux Command Library](https://linuxcommandlibrary.com/)
