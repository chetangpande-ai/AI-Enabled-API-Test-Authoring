import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.testng.Assert;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;
import utilities.ExtentTestManager; // Assume this class exists for generating ExtentReports

public class UsersTest {

    @BeforeClass
    public void setup() {
        RestAssured.baseURI = "http://api.sample.com";
        ExtentTestManager.logInfo("Base URI set to: " + RestAssured.baseURI);
    }

    @Test
    public void verifyGetUsersReturnsListOfUsersSuccessfully() {
        String testObjective = "Verify GET /users returns list of users successfully";

        // Logging test objective
        ExtentTestManager.logInfo("Starting test: " + testObjective);

        // Act
        ExtentTestManager.logInfo("Sending GET request to /users");
        Response response = RestAssured
                .given()
                .header("Accept", "application/json")
                .when()
                .get("/users");

        // Assert
        ExtentTestManager.logInfo("Verifying status code is 200");
        Assert.assertEquals(response.getStatusCode(), 200, "Expected HTTP status code is 200");
        ExtentTestManager.logInfo("Verifying response body contains a list of users");
        Assert.assertTrue(response.getBody().jsonPath().getList("$").size() > 0, "Response should contain a list of users");

        ExtentTestManager.logPass("Test passed successfully");
    }

    @Test
    public void verifyPostUsersFailsWhenNameIsMissing() {
        String testObjective = "Verify POST /users fails with 400 when name is missing";

        // Logging test objective
        ExtentTestManager.logInfo("Starting test: " + testObjective);

        // Arrange
        String payload = "{ \"email\": \"test@example.com\" }";

        // Act
        ExtentTestManager.logInfo("Sending POST request to /users with payload: " + payload);
        Response response = RestAssured
                .given()
                .header("Content-Type", "application/json")
                .body(payload)
                .when()
                .post("/users");

        // Assert
        ExtentTestManager.logInfo("Verifying status code is 400");
        Assert.assertEquals(response.getStatusCode(), 400, "Expected HTTP status code is 400");
        ExtentTestManager.logInfo("Verifying response body contains an error message for missing name");
        Assert.assertTrue(response.getBody().asString().contains("name is required"), "Error message should mention 'name is required'");

        ExtentTestManager.logPass("Test passed successfully");
    }

    @Test
    public void verifyPostUsersFailsWhenBothFieldsAreMissing() {
        String testObjective = "Verify POST /users fails with 400 when name and email are missing";

        // Logging test objective
        ExtentTestManager.logInfo("Starting test: " + testObjective);

        // Arrange
        String payload = "{}";

        // Act
        ExtentTestManager.logInfo("Sending POST request to /users with payload: " + payload);
        Response response = RestAssured
                .given()
                .header("Content-Type", "application/json")
                .body(payload)
                .when()
                .post("/users");

        // Assert
        ExtentTestManager.logInfo("Verifying status code is 400");
        Assert.assertEquals(response.getStatusCode(), 400, "Expected HTTP status code is 400");
        ExtentTestManager.logInfo("Verifying response body contains an error message for missing fields");
        Assert.assertTrue(response.getBody().asString().contains("name") && response.getBody().asString().contains("email"), "Error message should mention missing 'name' and 'email' fields");

        ExtentTestManager.logPass("Test passed successfully");
    }

    @Test
    public void verifyPostUsersFailsWhenEmailFormatIsInvalid() {
        String testObjective = "Verify POST /users fails with 400 when format of email is incorrect";

        // Logging test objective
        ExtentTestManager.logInfo("Starting test: " + testObjective);

        // Arrange
        String payload = "{ \"name\": \"John Doe\", \"email\": \"invalid-email\" }";

        // Act
        ExtentTestManager.logInfo("Sending POST request to /users with payload: " + payload);
        Response response = RestAssured
                .given()
                .header("Content-Type", "application/json")
                .body(payload)
                .when()
                .post("/users");

        // Assert
        ExtentTestManager.logInfo("Verifying status code is 400");
        Assert.assertEquals(response.getStatusCode(), 400, "Expected HTTP status code is 400");
        ExtentTestManager.logInfo("Verifying response body contains error message for invalid email");
        Assert.assertTrue(response.getBody().asString().contains("invalid email"), "Error message should mention invalid email");

        ExtentTestManager.logPass("Test passed successfully");
    }

    @Test
    public void verifyPostUsersHandlesEmailCaseSensitivity() {
        String testObjective = "Verify POST /users handles case sensitivity correctly";

        // Logging test objective
        ExtentTestManager.logInfo("Starting test: " + testObjective);

        // Arrange - First request
        String payload1 = "{ \"name\": \"John Doe\", \"email\": \"Test@Example.com\" }";

        // Act - First request
        ExtentTestManager.logInfo("Sending first POST request to /users with payload: " + payload1);
        Response response1 = RestAssured
                .given()
                .header("Content-Type", "application/json")
                .body(payload1)
                .when()
                .post("/users");

        // Assert - First request
        ExtentTestManager.logInfo("Verifying first response status code is 201");
        Assert.assertEquals(response1.getStatusCode(), 201, "Expected HTTP status code is 201 for first request");

        // Arrange - Second request
        String payload2 = "{ \"name\": \"John Doe\", \"email\": \"test@example.com\" }";

        // Act - Second request
        ExtentTestManager.logInfo("Sending second POST request to /users with payload: " + payload2);
        Response response2 = RestAssured
                .given()
                .header("Content-Type", "application/json")
                .body(payload2)
                .when()
                .post("/users");

        // Assert - Second request
        ExtentTestManager.logInfo("Verifying second response status code is 201");
        Assert.assertEquals(response2.getStatusCode(), 201, "Expected HTTP status code is 201 for second request");

        ExtentTestManager.logPass("Test passed successfully");
    }
}