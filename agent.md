# AI Instructions

This is a project for better understanding bank account spendings and incomes through graphs and additional features. The data is obtained from CSVs obtained from Revolut. AI in this project will be used to program UI.

## Coding Standards

  - The UI must adhere to a modern simple style. Inspiration should be taken from Apple. The UI should be fast and the code should be easy to read and straight forward code should be prioritized.

  - Code should be written and structured such that the programmer has to memorize the least amount of facts possible. Project insights should not have to be remembered by the developer, they should be relayed on features like good code quality, tests, uniform and good code organization in functions, classes, files and directories, etc.

  - Code readability is paramount, the ideal goal is that the project can easily be understood with a quick look at the code.

## Code Structure
```
.
├── app.py              # Entry point of the application
├── assets/             # Global CSS and static assets
├── data/               # User-specific bank data (CSV/JSON/etc.)
├── src/                # Main source code
│   ├── entities/       # Domain classes and data objects
│   ├── services/       # Core business logic
│   │   └── analytics/  # Specialized logic for data computation
│   └── storage/        # Database access layer (API/Repository)
│       └── models/     # Database schemas and ORM definitions
└── tests/              # Test suites (mirrors src/ structure)
```

## Rules

  - Never modify code in `src/` directory without previous consent.

## AI Notes

This is a section for the agent to add notes in a structured format to serve as persistent memory. Whenever the developer mentions a rule or pattern that is worth noting this is the place where to do so.

- Intended app features found from the code/tests: import Revolut CSV exports, persist them in `data/global.csv`, skip overlapping transactions, report date gaps when imports do not connect cleanly, filter transactions by date range, group income/outcome/balance by day/week/month/year, visualize cash flow, and inspect the underlying transactions.
