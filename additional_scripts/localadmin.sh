#!/bin/bash

# Default values
output_file="localadmin.txt"

# Help function
usage() {
    echo "Usage: $0 -u <username> -p <password> -d <domain> -i <input_file> [-o <output_file>]"
    echo "Options:"
    echo "  -u <username>    Username for authentication"
    echo "  -p <password>    Password for authentication"
    echo "  -d <domain>      Domain for authentication"
    echo "  -i <input_file>  Input file with list of IP addresses/hostnames"
    echo "  -o <output_file> Output file to save results (default: localadmin.txt)"
    echo "  -h               Show this help message"
    exit 1
}

# Parse arguments
while getopts "u:p:d:i:o:h" opt; do
    case $opt in
        u) username="$OPTARG";;
        p) password="$OPTARG";;
        d) domain="$OPTARG";;
        i) input_file="$OPTARG";;
        o) output_file="$OPTARG";;
        h) usage;;
        *) usage;;
    esac
done

# Check required arguments
if [[ -z "$username" || -z "$password" || -z "$domain" || -z "$input_file" ]]; then
    echo "Error: Missing required arguments!"
    usage
fi

# Check if input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' not found!"
    exit 1
fi

# Clear output file if it exists
> "$output_file"

# Process each line from input file
while read -r line; do
    echo "[+] $line"
    
    # Execute net rpc command and capture output
    result=$(net rpc group members "Administrators" -U "$domain"/"$username"%"$password" -I "$line" 2>&1)
    
    echo "$result"
    echo
    
    # Save results to output file
    echo "[+] $line" >> "$output_file"
    echo "$result" >> "$output_file"
    echo >> "$output_file"
    
     # Execute net rpc command and capture output
    result=$(net rpc group members "Администраторы" -U "$domain"/"$username"%"$password" -I "$line" 2>&1)
    
    echo "$result"
    echo
    
    # Save results to output file
    echo "[+] $line" >> "$output_file"
    echo "$result" >> "$output_file"
    echo >> "$output_file"
    
done < "$input_file"

echo "Scan completed. Results saved to $output_file"
