# Special Copilot Instructions for Anytime_Fitness_Bot_Modular

## 🏗️ Repository Purpose

This repository implements a modular gym management automation system for Anytime Fitness. It integrates with ClubHub, Square, and Gemini AI to automate token extraction, payment processing, member communication, and more.

## 🗂️ Folder and Module Structure

- `config/`  
  - `constants.py`, `secrets.py`: App settings, secret management.
- `core/`  
  - `authentication.py`, `driver.py`: Auth/session, browser driver utilities.
- `services/`  
  - `ai/`: Gemini AI integration.
  - `api/`: API clients for ClubHub, Square, etc.
  - `authentication/`: Token extraction/management.
  - `calendar/`: Scheduling integrations.
  - `clubos/`: ClubOS messaging and features.
  - `data/`: Data management, CSV/Excel.
  - `notifications/`: Multi-channel notifications.
  - `payments/`: Square payment processing.
- `workflows/`  
  - Main business logic and automation workflows (e.g., payment, messaging).
- `utils/`  
  - Common helpers, debugging utilities.
- `web/`  
  - Flask app, routes, webhooks.
- `data/`, `logs/`, `tests/`, `docs/`, `scripts/legacy/`, `backup/`:  
  - Data, logs, tests, documentation, archived scripts, backups, etc.
- `main.py`: Application entry point.
- `smart_token_capture.py`: Automated token extraction.

## 🧑‍💻 Coding Conventions

- **Language:** Python (primary), with some HTML for templates/UI.
- **Style:** PEP8 for Python; use type hints where possible.
- **Modularity:** Each feature/integration lives in its own subfolder/module.
- **Service Layer:** All external integrations through `services/`.
- **Workflows:** Orchestrate business logic using well-named scripts in `workflows/`.
- **Configuration:** All secrets/configs in `config/`; never hardcode secrets.

## 🏷️ Naming & Patterns

- Prefer descriptive, snake_case names for Python files and functions.
- Place all new integrations in the appropriate `services/` subfolder.
- Centralize shared logic in `utils/` or `core/`.
- Each workflow should be in its own script in `workflows/`, named for its function.
- For new features, create a matching test in `tests/`.

## 📝 Copilot-Specific Instructions

- When generating new modules, use the established folder structure.
- Always import shared helpers/utilities from `utils/` or `core/`.
- For new integrations, follow the pattern of `services/<integration>/`.
- Add documentation for new modules in `docs/` and, if needed, a README in the module folder.
- Use `.env` and `config/secrets.py` for all credentials and keys.
- Place all debug, log, and error files in `logs/`.
- If workflow automation is needed, create or extend a script in `workflows/`.

## 🧪 Testing

- All new features should have corresponding tests in `tests/`.
- Use `pytest` conventions for test file and function names.
- Mock external service calls in tests.

## 🔒 Security

- Never commit real secrets; use `config/secrets.py` and environment configs.
- Store credentials in Google Cloud Secret Manager if possible.

---

*Reference main docs in `/docs/README.md` and `/docs/PROJECT_OVERVIEW.md` for more details.*