# omni-svg-morph - Quick Start Guide

## 1. Install
omni get omni-svg-morph

## 2. Initialize
import { init } from '@omni/omni-svg-morph'
let instance = init(Config::from_env())?

## 3. Use
let result = instance.execute(data)?

## 4. Deploy
omni build --release
omni cloud deploy