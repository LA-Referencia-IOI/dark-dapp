---
description: Apply the AGPLv3 Public Infrastructure licensing model to a project.
---

This workflow applies the AGPLv3 licensing model to the current project, establishing it as public digital infrastructure.

## 1. Create LICENSE file
Create a `LICENSE` file in the root directory with the content of the **GNU Affero General Public License v3.0**.
If the file exists, ask the user before overwriting.

## 2. Create CONTRIBUTING.md
Create a `CONTRIBUTING.md` file with the following content. This ensures all contributions are compatible with the AGPLv3 license.

```markdown
# Contributing

Thank you for your interest in contributing! This project is designed as **public, federated digital infrastructure**, and your contributions help ensure it remains sustainable and accessible.

## Licensing of Contributions

By submitting a pull request or other contribution, you agree to license your contribution under the **GNU Affero General Public License v3.0 (AGPLv3)**.

### What this means for you
*   Your code remains open source and credited to you.
*   The project can continue to be used by public and academic institutions freely.

## How to Contribute

1.  **Fork** the repository.
2.  **Create** a feature branch (`git checkout -b feature/amazing-feature`).
3.  **Commit** your changes (`git commit -m 'Add amazing feature'`).
4.  **Push** to the branch (`git push origin feature/amazing-feature`).
5.  **Open** a Pull Request.

Please ensure your code follows the project's coding standards and includes appropriate tests.
```

## 3. Update README.md
Add the following "Licensing" section to `README.md`. Adjust the placement to be near the end of the file or where appropriate.

```markdown
## License

### Software License
The source code is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)**.
*   **Conditions**: You are free to use, modify, and distribute the software without cost, provided that any network services you offer based on this software also make their source code available to users (closing the "ASP loophole").
*   See the [LICENSE](LICENSE) file for the full text.

### Documentation License
New documentation and non-code assets found in this repository are licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**. This allows for broad sharing and adaptation of the educational materials.
```

## 4. Update Source File Headers
Scan the project for source code files (e.g., `.sol`, `.py`, `.js`, `.ts`, `.rs`, `.go`).
Add or update the SPDX license identifier at the top of each file:

```
// SPDX-License-Identifier: AGPL-3.0
```

(Use the appropriate comment syntax for the language, e.g., `#` for Python).

## 5. Verification
- Verify `LICENSE` contains the AGPLv3 text.
- Verify `CONTRIBUTING.md` exists and contains the licensing clause.
- Verify `README.md` clearly states the AGPLv3 license.
- Spot check a few source files for the SPDX header.
