# Distributed Token Ring Simulator

A beginner-friendly Python GUI project for a Distributed Computing mini-project. It demonstrates token passing and mutual exclusion among five logical processes.

## Features

- Five logical processes: P1, P2, P3, P4, P5
- Circular ring topology with directional arrows
- One token, initially held by P1
- Automatic simulation and manual single-step mode
- Requests from a selected process or random process
- Visual states for token holder, waiting requests, and critical-section access
- Event log and simulation statistics
- Reset control
- Uses only Python's standard library (Tkinter)

## Requirements

- Python 3.10 or newer recommended
- Tkinter (normally included with standard Python installations)

No `pip install` is required.

## How to run

1. Extract the ZIP file.
2. Open a terminal in the project folder.
3. Run:

   ```bash
   python main.py
   ```

   On some Windows installations, use:

   ```bash
   py main.py
   ```

4. Click **Request Resource** or select a process and click **Submit Request**.
5. Click **Pass Token (One Step)** to advance manually, or **Start Auto Simulation** to run automatically.
6. Watch the node colors and Event Log.

## How to use the simulator

- **Yellow node:** currently holds the token.
- **Pink node:** has a pending request.
- **Green node:** is inside the critical section.
- **Waiting queue:** processes that have requested the resource.
- **Token passes:** number of simulation steps recorded.
- **Completed resource accesses:** number of completed critical-section visits.

## Project scope and limitation

This is a *simulator* of a distributed token-ring algorithm. The nodes are logical processes represented in one Python GUI, not independent computers communicating over a real network. It is suitable for demonstrating the algorithm. A networked extension could run each process separately and pass token messages over TCP sockets.

## Core algorithm

1. Arrange N processes in a logical ring.
2. Give the token to one process initially.
3. Each process may request the shared resource.
4. The token circulates in order.
5. A process can enter the critical section only when it holds the token and has a pending request.
6. It releases the resource, then passes the token to its successor.
7. The successor is `(current_index + 1) % number_of_processes`.

## Troubleshooting

- If `tkinter` cannot be imported, install the Python distribution that includes Tcl/Tk. On Windows, the official Python installer typically offers Tcl/Tk support.
- If the command `python` is not recognized on Windows, try `py main.py`.
