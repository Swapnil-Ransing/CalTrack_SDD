# Structure Steering

## Repo layout (target — grows phase by phase, don't pre-create unused folders)

```
/
├── .claude/                   # this scaffold
├── .streamlit/
│   ├── config.toml            # theme
│   └── secrets.toml.example   # documents required secret keys (real file is gitignored)
├── app.py                     # entrypoint / home page
├── pages/                     # Streamlit auto-discovers pages here
│   ├── 1_💧_Water.py
│   ├── 2_🍽️_Meals.py
│   └── ...                    # numbered + emoji-prefixed for sidebar order/icons
├── services/                  # gemini client, calorie calc, db access
├── models/                    # SQLAlchemy models
├── schemas/                   # Pydantic schemas (incl. Gemini response schemas)
├── core/                      # config (st.secrets wrapper), db session, auth helpers
├── components/                # reusable UI helpers (cards, CSS injection)
├── alembic/
├── tests/
├── requirements.txt
├── docker-compose.yml         # local Postgres for dev
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
- Streamlit page files: `<order>_<emoji>_<Title>.py` (e.g. `2_🍽️_Meals.py`)
- DB tables: `snake_case`, plural (e.g. `nutrition_log`, `water_log`, …)
