- ## Overview

  These guidelines define mandatory practices for developing, running, and maintaining LRGEX web applications. They are designed for **human developers** and **agentic AI assistants** to operate seamlessly in a consistent, safe, and predictable environment.

  The document covers:

  1. Development Environment & Tooling
  2. Python Environment Management
  3. Git & Version Control Safety
  4. Self-Debugging & Logging

  ------

  ## 1. Development Environment & Tooling

  ### 1.1 Server & Port Configuration

  **Objective:** Prevent port conflicts, maintain session stability, and enforce clear resource usage.

  **Frontend Development:**

  - Use hot-reloadable servers only (e.g., Vite, Webpack).
  - Port persistence is mandatory:
    - Reuse the **same port** throughout the session.
    - Before starting, ask the user for their preferred port.
    - If no input, use default port (3000 recommended).
  - Only **one frontend instance** may run per project session.

  **Backend Development:**

  - The backend must always run on **Port 8000**.
  - Only **one backend instance** may run per project session.
  - Ensure no simultaneous frontend/backend duplication.

  **Resource Management Rules:**

  - **1:1 Architecture Enforcement:** Maximum one frontend and one backend instance active at any time.
  - Automatically terminate existing server instances if new instance is requested on the same role/port.

  ------

  ### 1.2 Python Environment Management

  **Objective:** Standardize Python dependencies and environment handling across all LRGEX projects.

  **Environment Tooling:**

  - All Python projects must use **uv** exclusively for environment management.

  **Commands & Protocols:**

  - Initialization:

  ```bash
  uv init
  ```

  - Add dependency:

  ```bash
  uv add <package>
  ```

  - Remove dependency:

  ```bash
  uv remove <package>
  ```

  - Run scripts/servers:

  ```bash
  uv run <script.py>
  ```

  **Agentic AI Behavior:**

  - Never modify environments without explicit instruction.
  - Verify UV-managed dependencies before execution.
  - Avoid global pip/conda modifications unless the user explicitly permits them.

  ------

  ### 1.3 Git & Version Control Safety

  **Objective:** Prevent accidental loss or corruption of project history.

  **Mandatory Rules:**

  - **No automatic commits:** Never commit or push changes unless explicitly instructed.
  - **No automatic restores:** Never use `git restore`, `git checkout`, or `git reset` without user permission.
  - **Manual control required:** All Git actions must be initiated by the user.
  - Always confirm the target branch and remote before performing any Git operation.

  ------

  ### 1.4 Self-Debugging & Logging

  **Objective:** Enable autonomous problem-solving by leveraging server logs instead of user input.

  **Logging Practices:**

  - Start all servers with **verbose logging** (DEBUG level recommended).
  - Monitor stdout/stderr continuously for errors.
  - Analyze stack traces internally before querying the user.
  - Only request user input if the issue is purely **visual/CSS-related** and cannot be inferred from logs.

  **AI Responsibilities:**

  - Parse logs automatically to detect runtime errors.
  - Apply corrective actions autonomously when possible.
  - Maintain internal error history for trend analysis.

  **1.5 Modular Architecture (Mandatory)**

  **Objective:** Guarantee that web applications are fully modular, maintainable, and scalable.

  - No feature shall reside in a single monolithic file.
  - Each feature must be encapsulated in its own independent file, fully self-contained.
  - Modules interact only through a designated **glue layer**, ensuring clean separation and no unintended dependencies.
  - **Adding a feature:** Create its module file and register it in the glue layer—instant integration.
  - **Removing a feature:** Delete its module file—no impact on the rest of the application.
  - The architecture must support **seamless feature expansion or removal**, maintaining full functionality at all times.

  **Key Principle:** Every module is plug-and-play, ensuring the application evolves without risk of regressions or entanglement.

  ------

  ## ✅ Key Takeaways

  - **Single-instance architecture:** 1 frontend, 1 backend, 1 persistent port per role.
  - **Uv-centric Python management:** no pip/conda outside uv unless approved.
  - **Strict Git discipline:** user-controlled commits, pushes, and resets only.
  - **Self-debug first:** server logs > user browser data.