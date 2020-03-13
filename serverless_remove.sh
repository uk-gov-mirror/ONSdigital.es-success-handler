#!/usr/bin/env bash

cd success-handler-repository
echo Installing dependancies
serverless plugin install --name serverless-latest-layer-version
echo Destroying serverless bundle...
serverless remove --verbose;
