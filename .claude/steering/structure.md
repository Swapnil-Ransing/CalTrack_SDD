# Structure Steering

## Repo layout (target — grows phase by phase, don't pre-create unused folders)

```
/
├── .claude/                 # this scaffold
├── frontend/                 # Next.js app
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── tests/
├── backend/                  # FastAPI app
│   ├── app/
│   │   ├── api/              # route handlers
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas (incl. Gemini response schemas)
│   │   ├── services/          # gemini client, calculations, etc.
│   │   └── core/              # config, db session, auth
│   ├── alembic/
│   └── tests/
├── docker-compose.yml
└── docs/
    └── deployment.md
```

## Phase spec layout

Each phase gets one folder under `.claude/specs/phases/`, numbered:

```
.claude/specs/phases/04-voice-logging/
├── requirements.md
├── design.md
└── tasks.md
```

Numbering is sequential and matches the roadmap. Never reuse or renumber a phase folder
once it has shipped — if scope changes later, that's a new phase.

## Naming
- Python: `snake_case` modules/functions, `PascalCase` classes
- TypeScript/React: `PascalCase` components, `camelCase` functions/vars
- DB tables: `snake_case`, plural (e.g. `nutrition_log`, `water_log`, …)
