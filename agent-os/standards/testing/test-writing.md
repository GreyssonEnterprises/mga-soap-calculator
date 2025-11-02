## Test coverage standards

- **TDD Cycle Is Law**: For every new feature or bug fix, write a failing test first (RED), implement the minimal code to pass it (GREEN), then refactor while keeping the suite green (REFACTOR).
- **Edge Cases Included**: Cover nominal paths, edge conditions, error states, and validation failures. If it can break, write a test proving it doesnt.
- **Executable Specs**: Tests express requirements. Favor high-signal assertions that describe behavior, not implementation details.
- **Fixture Discipline**: Use factories/builders to keep setups explicit and maintainable. Hidden magic in global fixtures is banned.
- **Integration & Contract Tests**: Where modules interact, add integration tests or consumer-driven contract tests to prove boundaries hold.
- **Mock With Intent**: Stub only true externals (network, filesystem, third-party APIs). Avoid mocking your own code; refactor instead.
- **Performance of the Suite**: Keep unit tests sub-second and integration tests parallelizable. If a test is slow, optimize or mark it appropriately.
- **Regression Shields**: Every discovered bug gets a test that reproduces the failure and stays in the suite permanently.
- **Coverage Gates**: Maintain statement/branch coverage thresholds agreed per project. Dropping below requires immediate remediation before merge.
