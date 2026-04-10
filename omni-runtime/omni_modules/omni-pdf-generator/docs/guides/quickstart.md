# omni-pdf-generator - Quick Start Guide

## 1. Install
omni get omni-pdf-generator

## 2. Initialize
import { init } from '@omni/omni-pdf-generator'
let instance = init(Config::from_env())?

## 3. Use
let result = instance.execute(data)?

## 4. Deploy
omni build --release
omni cloud deploy