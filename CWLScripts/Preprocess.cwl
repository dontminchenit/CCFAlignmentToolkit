#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool


requirements:
  DockerRequirement:
    dockerPull: "ccfalignmenttoolkit"
    dockerOutputDirectory: /data/output
  SubworkflowFeatureRequirement: {}

baseCommand: ["python3", "/opt/src/Preprocess.py"]
inputs:
  inputImage:
    type: File
    inputBinding:
      position: 1

outputs: 
  processedImage:  
    type: File
    outputBinding:
      glob: "*.nii.gz"
