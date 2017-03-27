# -*- coding: utf-8 -*-
"""This is a very basic python config file - just for testing"""
from __future__ import unicode_literals, print_function
from gcdt import gcdt_signals


CFG = {
  "ramuda": {
    "lambda": {
      "name": "infra-dev-sample-lambda-unittest",
      "description": "lambda test for ramuda",
      "role": "arn:aws:iam::420189626185:role/7f-selfassign/infra-dev-CommonLambdaRole-CEQQX3SPUTFX",
      "handlerFunction": "handler.handle",
      "handlerFile": "handler.py",
      "timeout": 300,
      "memorySize": 256,
      "events": {
        "s3Sources": [
          {
            "bucket": "unittest-lambda-event",
            "type": "s3:ObjectCreated:*",
            "suffix": ".gz"
          }
        ],
        "timeSchedules": [
          {
            "ruleName": "infra-dev-sample-lambda-jobr-T1",
            "ruleDescription": "run every 5 min from 0-5",
            "scheduleExpression": "cron(0/5 0-5 ? * * *)"
          },
          {
            "ruleName": "infra-dev-sample-lambda-jobr-T2",
            "ruleDescription": "run every 5 min from 8-23:59",
            "scheduleExpression": "cron(0/5 8-23:59 ? * * *)"
          }
        ]
      },
      "vpc": {
        "subnetIds": [
          "subnet-d5ffb0b1",
          "subnet-d5ffb0b1",
          "subnet-d5ffb0b1",
          "subnet-e9db9f9f"
        ],
        "securityGroups": [
          "sg-660dd700"
        ]
      }
    },
    "bundling": {
      "zip": "bundle.zip",
      "folders": [
        {
          "source": "./vendored",
          "target": "."
        },
        {
          "source": "./impl",
          "target": "impl"
        }
      ]
    },
    "deployment": {
      "region": "eu-west-1",
      "artifactBucket": "7finity-infra-dev-deployment"
    }
  }
}


def dummy_handler():
    pass


def register():
    """Please be very specific about when your plugin needs to run and why.
    E.g. run the sample stuff after at the very beginning of the lifecycle
    """
    gcdt_signals.initialized.connect(dummy_handler)


def deregister():
    gcdt_signals.initialized.disconnect(dummy_handler)


def generate_config():
    return CFG
