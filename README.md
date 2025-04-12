# beautools

*this readme is gpt-generated*

## WORK IN PROGRESS

---

Cool utility library for Python that provides tools for:

- helper, utility functions
- logging and timing decorators
- periodic task cycling (sync and async)
- SQLAlchemy repository patterns and mixins

## Features

### 🧩 Decorators

Easy debugging and performance tracking

### 🔄 Cyclers

Automate repetitive tasks with:

- `Cycler`: sync loop with error handling and sleep intervals.
- `AsyncCycler`: asyncio-based version with same logic.

### 🗃️ DefaultRepo

Simple SQLAlchemy ORM pattern for:

- `get_first`, `get_all`, `get_or_create`
- session handling (sync & async)
- commit, delete, save helpers

### 🛠️ Repo Mixins

For ORM models:

- auto primary key (`UUIDPK_Mixin`, `SerialPK_Mixin`)
- created/modified timestamp mixins
- `auto_repr()` utility for readable `__repr__`

### 📁 File I/O

Helpers for loading config:

- `read_yaml(path)`
- `read_json(path)`
- `YamlFile` class for ordered YAML parsing and saving

### 🧪 Utilities

Small handy functions:

- safe dictionary access (`get_or_first`, `reverse_dict`)
- chained mappers (`map_many`, `applyer`)
- list/dict transformations (`merge`, `mapl`, `mapc`)

## Installation

```bash
pip install beautools
