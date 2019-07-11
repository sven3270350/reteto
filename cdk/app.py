#!/usr/bin/env python3

from aws_cdk import core

from reteto.ci_stack import CIStack


app = core.App()
CIStack(app, "reteto-ci", bucket_name="artifacts.reteto.com")

app.synth()
