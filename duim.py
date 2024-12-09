#!/usr/bin/env python3

import subprocess, sys
import argparse

'''
OPS445 Assignment 2
Program: duim.py 
Author: Prabhnoor Singh
The python code in this file (duim.py) is original work written by
Prabhnoor Singh. No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This script improves upon the Linux 'du' command by providing an easy-to-read 
visualization of directory usage with percentages, bar graphs, and optional human-readable output.

Semester: FALL 2024
Date: 8th December 2024
'''

def parse_command_args():
    """
    This function sets up the command-line arguments for the script.
    It allows users to:
    - Specify the graph length (-l).
    - Request human-readable sizes (-H).
    - Provide a target directory (default is the current directory).
    I used argparse here because it's better than sys.argv for handling optional arguments and provides a built-in help message.
    """
    parser = argparse.ArgumentParser(description="DU Improved -- See Disk Usage Report with bar charts", epilog="Copyright 2024")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Print sizes in human readable format (e.g., 1K, 23M, 2G)")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("target", nargs="?", default=".", help="The directory to scan. Defaults to the current directory.")
    args = parser.parse_args()
    return args


def percent_to_graph(percent: int, total_chars: int) -> str:
    """
    Converts a percentage into a visual bar graph using '=' symbols.
    - This is useful because visualizing the data helps understand the relative usage better.
    - The length of the graph is controlled by the user with the -l option.
    """
    if 0 <= percent <= 100:  # Ensure the input percentage is valid
        filled_length = round((percent / 100) * total_chars)  # Calculate how many '=' symbols should represent the filled part
        bar = '=' * filled_length + ' ' * (total_chars - filled_length)  # The rest of the bar is filled with spaces
        return bar
    else:
        return "Invalid Percentage"  # Handle invalid percentages gracefully


def call_du_sub(location: str) -> list:
    """
    This function runs the 'du -d 1' command to get disk usage information for the specified location.
    - The '-d 1' option ensures we only look at the first level of subdirectories, as required.
    - The subprocess module is used to execute the command and capture the output.
    - If there are "Permission denied" errors, they are ignored so the script can keep running.
    """
    try:
        process = subprocess.Popen(['du', '-d', '1', location], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            return stdout.splitlines()  # Split the output into a list of lines for easier processing
        else:
            # If there are errors, filter out "Permission denied" messages to avoid cluttering the output
            error_lines = stderr.splitlines()
            for line in error_lines:
                if "Permission denied" not in line:
                    print(f"Error: {line}")  # Print non-permission-related errors
            return stdout.splitlines()
    except Exception as e:
        print(f"Error executing subprocess: {e}")
        return []


def create_dir_dict(raw_data: list) -> dict:
    """
    This function takes the output from 'du' and converts it into a dictionary.
    - Each key is a directory path, and the value is its size in KiB.
    - Using a dictionary makes it easier to calculate totals and percentages later.
    """
    dir_dict = {}
    for line in raw_data:
        parts = line.split(None, 1)  # Split each line into size and path
        if len(parts) == 2:
            size = int(parts[0])  # Convert the size to an integer for calculations
            path = parts[1]  # The second part is the directory path
            dir_dict[path] = size
    return dir_dict


def bytes_to_human_r(kibibytes: int, decimal_places: int = 2) -> str:
    """
    Converts a size in KiB into a human-readable format like MiB or GiB.
    - This is necessary for the -H option, which makes the output more user-friendly.
    - I used a loop to divide the size until it fits into a human-readable unit.
    """
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    suffix_index = 0
    size = kibibytes
    while size >= 1024 and suffix_index < len(suffixes) - 1:
        size /= 1024
        suffix_index += 1
    return f"{size:.{decimal_places}f} {suffixes[suffix_index]}"


def colour(percentage: int) -> str:
    """
    Adds color to the output based on the usage percentage:
    - Red for high usage (>75%).
    - Yellow for moderate usage (>50%).
    - Cyan for low usage (>25%).
    - Green for minimal usage (<25%).
    This makes it easier to identify heavily used directories at a glance.
    """
    if percentage > 75:
        return "\033[91m"  # Red
    elif percentage > 50:
        return "\033[93m"  # Yellow
    elif percentage > 25:
        return "\033[96m"  # Cyan
    else:
        return "\033[92m"  # Green


if __name__ == "__main__":
    """
    The main function ties everything together:
    - Parses the command-line arguments.
    - Fetches directory data using 'du'.
    - Calculates percentages and generates bar graphs.
    - Displays the results in a clear and colorful format.
    """
    args = parse_command_args()

    raw_data = call_du_sub(args.target)
    if not raw_data:
        print("Error: Unable to fetch directory data. Please check the target directory.")
        sys.exit(1)

    dir_dict = create_dir_dict(raw_data)
    total_size = sum(dir_dict.values())  # The total size is needed to calculate percentages

    for path, size in dir_dict.items():
        percentage = (size / total_size) * 100  # Calculate the percentage of the total size
        graph = percent_to_graph(percentage, args.length)  # Generate the bar graph
        size_display = bytes_to_human_r(size) if args.human_readable else f"{size} KiB"  # Format the size
        color = colour(percentage)  # Get the appropriate color for the percentage
        print(f"{color}{percentage:>3.0f}% [{graph}] {size_display:>10} {path}\033[0m")  # Print the output
