#!/bin/bash

# Function to delete files in a directory except .gitkeep
delete_except_gitkeep() {
    local dir=$1
    if [ -d "$dir" ]; then
        find "$dir" -mindepth 1 ! -name ".gitkeep" -delete
    else
        echo "Directory $dir does not exist."
    fi
}

# Parse arguments
DELETE_LOGS=false
DELETE_RESULTS=false
DELETE_DATASET=false
DELETE_VENV=false

if [ $# -eq 0 ]; then
    DELETE_LOGS=true
    DELETE_RESULTS=true
fi

for arg in "$@"
do
    case $arg in
        --dataset)
        DELETE_DATASET=true
        shift
        ;;
        --venv)
        DELETE_VENV=true
        shift
        ;;
        --all)
        DELETE_LOGS=true
        DELETE_RESULTS=true
        DELETE_DATASET=true
        DELETE_VENV=true
        shift
        ;;
        *)
        DELETE_LOGS=true
        DELETE_RESULTS=true
        ;;
    esac
done

# Perform deletions based on flags
if [ "$DELETE_LOGS" = true ]; then
    delete_except_gitkeep "logs"
fi

if [ "$DELETE_RESULTS" = true ]; then
    delete_except_gitkeep "results"
fi

if [ "$DELETE_DATASET" = true ]; then
    delete_except_gitkeep "dataset"
fi

if [ "$DELETE_VENV" = true ]; then
    if [ -d "venv" ]; then
        rm -rf "venv"
    else
        echo "Directory venv does not exist."
    fi
fi

echo "Cleanup completed."
