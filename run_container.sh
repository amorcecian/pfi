#!/bin/bash
docker container run -p80:8080 -v $(pwd):/app/src --env-file .env -it aramcito 