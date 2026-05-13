# AI Instructions

This is a project for better understanding bank account spendings and incomes through graphs and additional features. The data is obtained from CSVs obtained from Revolut. AI in this project will be used to program UI.

## Coding Standards

  - The UI must adhere to a modern simple style. Inspiration should be taken from Apple's Liquid Glass yet easy to read and straight forward code should be prioritized.

  - Code should be written and structured such that the programmer has to memorize the least amount of facts possible. Project insights should not have to be remembered by the developer, they should be relayed on features like good code quality, tests, uniform and good code organization in functions, classes, files and directories, etc.

  - Code readability is paramount, the ideal goal is that the project can easily be understood with a quick look at the code.

## Code Structure
```
```
.
├── app.py              # starting point of the app
├── assets              # directory with CSS assets
├── data                # directory with user's bank data
├── src
│   ├── entities        # directory with classes used in the project
│   ├── services        # code with logic
│   │   └── analytics   # logic code strictly intended for computing analytics
│   └── storage         # code that serves as an api for database access
│       └── models      # contains database models
└── tests               # tests directory that mirrors the structure of the repo
```
```

## Rules

  - Never modify code in `src/` directory without previous consent.
  - Never modify any of this file's sections except the 'AI Notes' one.

## AI Notes

This is a section for the agent to add notes in a list form. Whenever the developer mentions a rule or pattern that is worth noting this is the place where to do so.
