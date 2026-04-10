# omni-aws-s3 - Quick Start Guide

## 1. Install
omni get omni-aws-s3

## 2. Initialize
import { init } from '@omni/omni-aws-s3'
let instance = init(Config::from_env())?

## 3. Use
let result = instance.execute(data)?

## 4. Deploy
omni build --release
omni cloud deploy