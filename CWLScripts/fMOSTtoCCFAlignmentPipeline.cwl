#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: Workflow
inputs:
  inputImage:
    type: File

  atlasDir:
    type: Directory

outputs:
  warpedMovingImage:
    type: File
    outputSource: register/imgWarpedToCCF

steps:
  preprocess:
    run: Preprocess.cwl
    in:
      inputImage: inputImage
    out: [processedImage]

  register:
    run: RegisterfMOST.cwl
    in:
      inputImage: preprocess/processedImage
      atlasDir: atlasDir
    out: [imgWarpedToCCF]
