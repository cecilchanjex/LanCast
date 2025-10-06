name: Build Android APK

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Cython
        run: pip install cython

      - name: Install dependencies
        run: pip install buildozer kivy opencv-python

      - name: Build APK
        run: buildozer android debug
