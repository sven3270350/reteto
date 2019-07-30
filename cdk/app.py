#!/usr/bin/env python3
from aws_cdk import core
from docker.docker_ci import DockerCIStack

app = core.App()
DockerCIStack(app, "reteto-ci", 
    repo= 'reteto',
    bucket_name= 'artifacts.reteto.com',
    create_bucket= True
)

app.synth()
