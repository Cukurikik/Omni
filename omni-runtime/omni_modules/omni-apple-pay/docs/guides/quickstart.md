# omni-apple-pay - Quick Start Guide

## 1. Install
omni get omni-apple-pay

## 2. Initialize
import { init } from '@omni/omni-apple-pay'
let instance = init(Config::from_env())?

## 3. Use
let result = instance.execute(data)?

## 4. Deploy
omni build --release
omni cloud deploy