# omni-digitalocean-spaces - Quick Start Guide

## 1. Install
omni get omni-digitalocean-spaces

## 2. Initialize
import { init } from '@omni/omni-digitalocean-spaces'
let instance = init(Config::from_env())?

## 3. Use
let result = instance.execute(data)?

## 4. Deploy
omni build --release
omni cloud deploy