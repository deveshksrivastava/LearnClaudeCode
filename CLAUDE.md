# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Mini FastAPI e-commerce API. Stack: Python, FastAPI, SQLite, Uvicorn. All code lives in `main.py`.

## Commands

```bash
# Install dependencies
pip install fastapi uvicorn

# Run the development server
uvicorn main:app --reload

# Run tests
pytest

# Run a single test
pytest tests/test_main.py::test_name -v
```
