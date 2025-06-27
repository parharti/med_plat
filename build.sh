#!/bin/bash
echo "==> Upgrading pip, setuptools, and wheel"
pip install --upgrade pip setuptools wheel

echo "==> Installing requirements.txt"
pip install -r requirements.txt
