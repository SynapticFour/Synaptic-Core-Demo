#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool
doc: |
  Documented CWL shape for the echo stand-in.
  Synaptic Core WES does not execute this file; it runs the `steps` array
  on POST /ga4gh/wes/v1/runs. workflow_url in the demo points at the TRS
  descriptor of the registered tool, not at this path.
baseCommand: [echo]
inputs:
  message:
    type: string
    default: ga4gh-demo-ok
    inputBinding: {}
outputs:
  out:
    type: stdout
stdout: out.txt
