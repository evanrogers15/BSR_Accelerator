#!/bin/bash

# Function to display help
function show_help() {
    echo "Usage: deploy.sh [OPTIONS]"
    echo "Deploy the bsr_accelerator container"
    echo ""
    echo "Options:"
    echo "  -d, --detach      Run the container in detached mode"
    echo "  --help            Display this help message"
    echo "  debug             Run the container in debug mode with bash"
}

# Function to stop and remove the existing container
function stop_existing_container() {
    existing_container=$(docker ps -a --filter "name=bsr_accelerator_test" --format '{{.Names}}' | grep -q '^bsr_accelerator_test$' && echo "true" || echo "false")
    if [ $existing_container == "true" ]; then
        echo "Stopping the existing bsr_accelerator_test container..."
        docker stop bsr_accelerator_test
        docker rm bsr_accelerator_test
    fi
}

# Check for the --help option
if [[ " $* " == *" --help "* ]]; then
    show_help
    exit 0
fi

# Stop and remove the existing container if it is running
stop_existing_container

# Check if the bsr_accelerator directory exists in the current directory
if [ -d "BSR_Accelerator" ]; then
    rm -rf BSR_Accelerator
fi

# Check if the bsr_accelerator directory exists in the parent directory
if [ -d "../BSR_Accelerator" ]; then
    rm -rf ../BSR_Accelerator
fi

# Clone the git project with the specified branch
git clone https://github.com/evanrogers15/BSR_Accelerator.git

# Navigate to the bsr_accelerator directory
cd BSR_Accelerator

# Build the Docker container with the test tag
docker build -t evanrogers719/bsr_accelerator:test .

# Check if the -d flag is passed
if [[ " $* " == *" -d "* ]]; then
    # Run the Docker container in detached mode with the specified port mapping(s) and container name
    docker run -d --name bsr_accelerator_test evanrogers719/bsr_accelerator:test
else
    # Run the Docker container in foreground with the specified port mapping(s) and container name
    docker run --name bsr_accelerator_test evanrogers719/bsr_accelerator:test
fi
