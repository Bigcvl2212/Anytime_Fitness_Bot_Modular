---
description: Repository Information Overview
alwaysApply: true
---

# Repository Information Overview

## Repository Summary
Gym-Bot is a modular automation system for gym management, primarily focused on integrating with ClubOS and providing features for member management, training scheduling, and payment processing. The repository contains multiple interconnected projects including a main dashboard application, a social media management bot, and a multi-club platform (MCP) server.

## Repository Structure
- **src/**: Core application code with modular services architecture
- **Social_Media_Management_Bot/**: Separate full-stack application for social media management
- **mcp-server/**: Multi-club platform server for managing multiple gym locations
- **config/**: Configuration files and credentials management
- **data/**: Data storage and exports
- **assets/**: Static assets for the application
- **cloud/**: Cloud deployment configurations

### Main Repository Components
- **Dashboard Application**: Flask-based web dashboard for gym management
- **ClubOS Integration**: Services for connecting with ClubOS API
- **Social Media Bot**: Full-stack application with React frontend and Python backend
- **MCP Server**: Multi-club platform server for centralized management

## Projects

### Main Dashboard Application
**Configuration File**: requirements.txt

#### Language & Runtime
**Language**: Python
**Version**: 3.11 (based on Dockerfile)
**Build System**: pip
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- Flask >= 2.0
- gunicorn >= 20.0
- beautifulsoup4 >= 4.9
- requests >= 2.25
- python-dotenv >= 1.0
- pandas >= 1.2
- lxml >= 4.6

#### Build & Installation
```bash
pip install -r requirements.txt
python wsgi.py  # Development
gunicorn --bind 0.0.0.0:5000 wsgi:app  # Production
```

#### Docker
**Dockerfile**: Dockerfile
**Image**: Python 3.11-slim
**Configuration**: Exposes port 5000, uses gunicorn as the WSGI server

#### Testing
**Framework**: Custom test scripts
**Test Location**: Root directory (test_*.py files)
**Naming Convention**: test_*.py
**Run Command**:
```bash
python test_calendar.py  # Example for specific test
```

### Social Media Management Bot
**Configuration File**: Social_Media_Management_Bot/backend/requirements.txt, Social_Media_Management_Bot/frontend/package.json

#### Language & Runtime
**Language**: Python (Backend), TypeScript/JavaScript (Frontend), React Native (Mobile)
**Build System**: pip (Backend), npm (Frontend/Mobile)
**Package Manager**: pip (Backend), npm (Frontend/Mobile)

#### Dependencies
**Backend**:
- Flask
- SQLAlchemy
- pytest

**Frontend**:
- Next.js
- React
- TypeScript

**Mobile**:
- React Native

#### Build & Installation
```bash
# Backend
cd Social_Media_Management_Bot/backend
pip install -r requirements.txt

# Frontend
cd Social_Media_Management_Bot/frontend
npm install
npm run build
npm start

# Mobile
cd Social_Media_Management_Bot/mobile
npm install
```

#### Docker
**Dockerfile**: Social_Media_Management_Bot/backend/Dockerfile, Social_Media_Management_Bot/frontend/Dockerfile
**Configuration**: Multi-container setup with nginx for frontend

#### Testing
**Framework**: pytest (Backend), Jest (Frontend/Mobile)
**Test Location**: Social_Media_Management_Bot/tests/, Social_Media_Management_Bot/frontend/__tests__/
**Run Command**:
```bash
# Backend
cd Social_Media_Management_Bot
python run_integration_tests.py

# Frontend
cd Social_Media_Management_Bot/frontend
npm test
```

### MCP Server
**Configuration File**: mcp-server/requirements.txt

#### Language & Runtime
**Language**: Python
**Build System**: pip
**Package Manager**: pip

#### Build & Installation
```bash
cd mcp-server
pip install -r requirements.txt
python gym-bot-mcp.py
```

#### Usage & Operations
**Key Commands**:
```bash
# Start server
cd mcp-server
./server-control.sh start

# Stop server
./server-control.sh stop
```