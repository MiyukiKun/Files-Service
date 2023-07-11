docker container rm -f fileservice-1
docker image rm fileservice
docker build -t fileservice .
docker run -d --name fileservice-1 fileservice