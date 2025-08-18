# How to Create a Compliant Pipeline

This document explains the requirements for creating a new processing pipeline that is compatible with the dashboard application.

## 1. Directory Structure

Each pipeline must be contained within its own directory inside this `pipelines/` folder. The name of the directory will be used as the unique identifier for the pipeline in the UI.

For example, a pipeline named `my-pipeline` would have the following structure:

```
pipelines/
└── my-pipeline/
    ├── Dockerfile
    └── process.sh
```

## 2. Dockerfile Requirements

Every pipeline directory **must** contain a `Dockerfile`. This file defines the environment and execution for your pipeline.

The `Dockerfile` has one critical requirement: it **must** use the `ENTRYPOINT` instruction to specify the script or command to be run. It **cannot** use `CMD`. This is because the server passes the input filename to the container as a command-line argument, and only `ENTRYPOINT` allows for this behavior correctly.

A minimal, compliant `Dockerfile` looks like this:

```dockerfile
FROM alpine:latest

# Set a working directory
WORKDIR /app

# Copy your script into the container
COPY process.sh .

# Make it executable
RUN chmod +x process.sh

# Set the entrypoint
ENTRYPOINT ["./process.sh"]
```

## 3. Handling Input

The server will provide the name of the uploaded file to your pipeline as a **command-line argument**. Your `ENTRYPOINT` script must be prepared to accept this argument.

The server also mounts the `uploads/` directory from the host machine to the `/data/` directory inside the container. Your script should look for the input file in `/data/`.

Here is an example of how to handle the input file in a shell script:

```bash
#!/bin/sh

# The input filename is the first argument
INPUT_FILENAME=$1

# The full path inside the container
FILE_PATH="/data/$INPUT_FILENAME"

# Always check if the file exists
if [ ! -f "$FILE_PATH" ]; then
  echo "Error: Input file not found at $FILE_PATH" >&2
  exit 1
fi

# Now you can use the file
echo "Processing file: $FILE_PATH"
```

## 4. Progress Reporting Standard

To make the UI's progress bar work, your pipeline script **must** print its progress to standard output (`stdout`) using a specific format.

The format is: `Steps: <current_step>/<total_steps> [<description>]`

*   `<current_step>`: The current step number (integer).
*   `<total_steps>`: The total number of steps for the entire process (integer).
*   `<description>`: A short, user-friendly string describing what is happening in the current step.

The server parses these lines to update the progress bar. Any other output from your script will be ignored by the progress parser (but it is logged by the server for debugging).

### Example Progress Reporting

```bash
#!/bin/sh
INPUT_FILENAME=$1
FILE_PATH="/data/$INPUT_FILENAME"

echo "Steps: 1/3 [Initializing]"
sleep 2

echo "Steps: 2/3 [Running core logic]"
# ... do some work ...
sleep 3

echo "Steps: 3/3 [Finalizing results]"
# ... clean up ...
sleep 1

# The job will be marked as "Completed" when the script exits with code 0.
```
