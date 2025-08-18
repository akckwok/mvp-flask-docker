# Use a small base image
FROM alpine:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the processing script into the container
COPY process.sh .

# Make the script executable
RUN chmod +x process.sh

# The command to run when the container starts
CMD ["./process.sh"]
