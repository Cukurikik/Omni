# omni-wasabi-s3 - Quick Start Guide

## 1. Install
omni get omni-wasabi-s3

## 2. Initialize
import { init } from '@omni/omni-wasabi-s3'
let instance = init(Config::from_env())?

## 3. Use
let result = instance.execute(data)?

## 4. Deploy
omni build --release
omni cloud deploy