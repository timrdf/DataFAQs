

# Run the service
./start.sh

# Issue a request to the service locally
wget --header "Content-type: text/turtle" --post-file sample-inputs/post.ttl http://localhost:9119/check

