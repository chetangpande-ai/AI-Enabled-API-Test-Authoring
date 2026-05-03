# Java Test Automation Framework Guidelines

## 1. Libraries and Tools
- **Test Runner**: TestNG (`@Test`, `@BeforeClass`, etc.)
- **API Client**: REST Assured (`given()`, `when()`, `then()`)
- **Assertions**: org.testng.Assert
- **Reporting**: ExtentReports. Use a custom `ExtentTestManager` (assume it exists) with `logInfo()`, `logPass()`, and `logFail()`.

## 2. Modularity and Structure
- Each major endpoint should have its own separate Test class (e.g., `ProductsTest.java`).
- Extract the Base URI into a `@BeforeClass` setup block.
- Keep tests modular: one `@Test` method per test case. Do not mix multiple scenarios into one test method.
- Clearly separate the Arrange, Act, and Assert phases.

## 3. Reporting Steps
- At the start of the test, log the objective: `ExtentTestManager.logInfo("Starting test: " + testObjective);`
- After executing the API request, log the action: `ExtentTestManager.logInfo("Sent POST request to /products");`
- Before assertions, log the expected outcome: `ExtentTestManager.logInfo("Verifying status code is 200");`
- If successful, log pass: `ExtentTestManager.logPass("Test passed successfully");`

## 4. Coding Standards
- Use proper Java naming conventions (camelCase for methods).
- Assume endpoints require no authentication unless specified.
- The generated code must be syntactically valid Java, ready to be dropped into a standard Maven/Gradle project.
