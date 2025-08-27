# Freckers 2


> ### Agent code is all our own.
> Each agent was written to be compatible with the 'referee' module and 'freckers' game provided by the University of Melbourne. 

---

## Overview

**Freckers 2** is part 2 of the Freckers assignment, which focuses on implementing autonomous (AI) game playing agents that interact with the 'freckers' game environment, following the specifications and referee module provided by the University of Melbourne.

## Features
- Agent implementations with heuristics of varying degrees of complexities
- Minimax with alpha-beta pruning
- Designed to be extensible and time effective

## Project Structure

- `agents/` – Contains all agent implementations
- `referee/` – (If included) Interface or utilities for interacting with the referee module
- `tests/` – Unit tests and integration tests for agent behavior
- `README.md` – Project documentation (this file)
- Other Python files – Core logic, helpers, and scripts for running or evaluating agents

## Requirements

- Python 3.7+

## Getting Started

1. **Clone the Repository**
   ```bash
   git clone https://github.com/jnakos01/freckers2.git
   cd freckers2
   ```
2. **Play the agents against each other**

## Usage

To use agents with the referee module:
```bash
python -m referee <red agent> <blue agent>
```
For the agents just add the agent module name.

## License

This project is intended for academic use. Please respect the University of Melbourne’s assignment policies.

---
