#!/bin/bash

# Parse command line flags
DOWNLOAD=false

while getopts "d" opt; do
    case $opt in
        d)
            DOWNLOAD=true
            ;;
        *)
            echo "Usage: $0 [-d]"
            echo "  -d: Download data files"
            exit 1
            ;;
    esac
done

# Only proceed with downloads if flag is set
if [ "$DOWNLOAD" = true ]; then
    echo "Downloading data files..."
    wget https://www.ssa.gov/oact/babynames/names.zip
    wget https://www.ssa.gov/oact/babynames/state/namesbystate.zip

    echo "Unzipping data files..."
    unzip names.zip -d data/
    unzip namesbystate.zip -d states_data/
fi
