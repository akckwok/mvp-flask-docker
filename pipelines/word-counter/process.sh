#!/bin/sh

# The input filename is passed as the first argument from the 'docker run' command.
INPUT_FILE=$1
FILE_PATH="/data/$INPUT_FILE"

echo "Steps: 1/3 [Initializing]"
sleep 1

# Basic validation to ensure the file exists in the container.
if [ ! -f "$FILE_PATH" ]; then
  echo "Error: Input file not found inside container at $FILE_PATH"
  exit 1
fi

echo "Steps: 2/3 [Counting Words]"
# Perform the actual word count.
WORD_COUNT=$(wc -w < "$FILE_PATH")
sleep 1

echo "Steps: 3/3 [Finalizing]"
echo "---"
echo "Word Count Result: $WORD_COUNT"
echo "---"
sleep 1

# The final "Steps: Y/Y" is not strictly needed, as the backend will
# mark the job as complete upon successful exit. But it's good practice.
# echo "Steps: 3/3 [Completed]"
