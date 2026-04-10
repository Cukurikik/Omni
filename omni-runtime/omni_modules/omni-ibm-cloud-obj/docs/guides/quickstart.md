# omni-ibm-cloud-obj - Quick Start Guide

## 1. Install
omni get omni-ibm-cloud-obj

## 2. Initialize
import { init } from '@omni/omni-ibm-cloud-obj'
let instance = init(Config::from_env())?

## 3. Use
let result = instance.execute(data)?

## 4. Deploy
omni build --release
omni cloud deploy