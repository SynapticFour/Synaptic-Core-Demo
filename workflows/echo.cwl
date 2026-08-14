#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool
doc: |
  Tiny CWL stand-in for Synaptic-Core-Demo GA4GH WES path.
  Real labs would point workflow_url at samtools/GATK CWL or Dockstore TRS.
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
