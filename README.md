
# J3ktMan - Project Manager

J3ktMan is an intuitive, web-based project management tool designed to streamline team collaboration, task tracking, and project planning. Tailored for agile workflows, J3ktMan offers a clean and powerful interface for managing projects, assigning tasks, and monitoring progress. The platform is ideal for small to medium-sized teams, startups, and freelancers looking for an efficient way to stay organized and productive.


## Features

- User authentication and role (e.g., admin, team member)
- Team collaboration on a project
- Kanban board & Gantt chart displaying tasks and their status
- Search and filtering (filter by assignee, priority or status) for tasks
- Dashboard summary of the project





## Tech Stack

**Reflex:** A full-stack Python framework handling both frontend and backend functionality

**Database:** PostgreSQL

**Authentication provider:** Clerk


## Installation

Requires python version >= 3.12.0

clone this repository

setup virtual environment

```bash
python3 -m venv .venv
```

activate virtual environment
```bash
source .venv/bin/activate
```
install required dependencies
```bash
pip install -e .
```

setup .env file
```.env
CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
DATABASE_URL=
```

migrate database 
```bash
reflex db migrate
```

run the app
```bash
reflex run
```

## Authors
- [Teemy17](https://github.com/Teemy17)
- [Umbs01](https://github.com/Umbs01)
- [Simmypeet](https://github.com/Simmypeet)


