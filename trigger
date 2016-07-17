#!/usr/bin/env bash
curl  -H 'Content-Type: application/json' -H  "Authorization: Bearer $WERCKER_TOKEN" -X POST -d '{"applicationId": "57853a9d5c41db32406bc706", "pipelineId": "57853a9d5c41db32406bc70a"}' https://app.wercker.com/api/v3/runs/
