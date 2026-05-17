# Design Rule

Design documents must be implementation-oriented.

## Required Sections

1. Overview
2. Data flow
3. Module responsibilities
4. File outputs
5. Error handling
6. Security considerations
7. Memory behavior
8. Tests
9. Compatibility
10. PlantUML diagrams when flow is complex

## Must Include

- How the design works without a database.
- How files are named and stored.
- What happens on partial failure.
- How the feature is disabled if optional.
- How future agents can continue development.

## Must Not Include

- Generic architecture theory.
- Undocumented dependencies.
- Broad unrelated refactoring.
