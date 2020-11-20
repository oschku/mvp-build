# start.sh
#!/bin/bash
app="docker.test3"
docker build -t ${app} .
docker run -d -p 5000:5000 \
  --name=${app} \
