## AgentFlow LangGraph Architecture

```text
User Request
     │
     ▼
┌─────────────┐
│   Router    │  ← reads `mode` field
└──────┬──────┘
       │
  ┌────┼────┐
  ▼    ▼    ▼
[sum][qa][tasks]   ← 3 specialist nodes
  │    │    │
  └────┴────┘
       │
       ▼
    Result