import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.testng.Assert;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;
import utils.ExtentTestManager;

public class UsersAPITest {

    private static final String BASE_URI = "https://api.example.com";

    @BeforeClass
    public void setUp() {
        RestAssured.baseURI = BASE_URI;
    }

    @Test
    public void verifyGetUsersFailsWith404WhenEndpointIsIncorrect() {
        String testObjective = "Verify GET /users fails with 404 when endpoint is incorrect";
        ExtentTestManager.logInfo("Starting test: " + testObjective);

        ExtentTestManager.logInfo("Sending GET request to '/user' (misspelled version of '/users').");
        Response response = RestAssured
                .given()
                .when()
                .get("/user")
                .then()
                .extract()
                .response();

        ExtentTestManager.logInfo("Verifying status code is 404.");
        Assert.assertEquals(response.getStatusCode(), 404, "Expected status code 404");

        String responseBody = response.getBody().asString();
        ExtentTestManager.logInfo("Verifying error message in the response body.");
        Assert.assertTrue(responseBody.contains("not found"), "Expected 'not found' in the error message.");

        ExtentTestManager.logPass("Test passed successfully");
    }

    @Test
    public void verifyPostUsersFailsWith422WhenEmailIsInvalid() {
        String testObjective = "Verify POST /users fails with 422 when email is invalid";
        ExtentTestManager.logInfo("Starting test: " + testObjective);

        // Test case 1: Invalid email "invalidemail@"
        String invalidEmailPayload1 = "{ \"name\": \"John Doe\", \"email\": \"invalidemail@\" }";
        ExtentTestManager.logInfo("Sending POST request to '/users' with invalid email: 'invalidemail@'.");

        Response response1 = RestAssured
                .given()
                .header("Content-Type", "application/json")
                .body(invalidEmailPayload1)
                .when()
                .post("/users")
                .then()
                .extract()
                .response();

        ExtentTestManager.logInfo("Verifying status code is 422.");
        Assert.assertEquals(response1.getStatusCode(), 422, "Expected status code 422");

        String responseBody1 = response1.getBody().asString();
        ExtentTestManager.logInfo("Verifying error message for invalid email.");
        Assert.assertTrue(responseBody1.contains("invalid email format"), "Expected error for invalid email format.");

        // Test case 2: Invalid email "test@.com"
        String invalidEmailPayload2 = "{ \"name\": \"Jane Doe\", \"email\": \"test@.com\" }";
        ExtentTestManager.logInfo("Sending POST request to '/users' with invalid email: 'test@.com'.");

        Response response2 = RestAssured
                .given()
                .header("Content-Type", "application/json")
                .body(invalidEmailPayload2)
                .when()
                .post("/users")
                .then()
                .extract()
                .response();

        ExtentTestManager.logInfo("Verifying status code is 422.");
        Assert.assertEquals(response2.getStatusCode(), 422, "Expected status code 422");

        String responseBody2 = response2.getBody().asString();
        ExtentTestManager.logInfo("Verifying error message for invalid email.");
        Assert.assertTrue(responseBody2.contains("invalid email format"), "Expected error for invalid email format.");

        ExtentTestManager.logPass("Test passed successfully");
    }

    @Test
    public void verifyPostUsersFailsWith422WhenNameExceedsMaxCharacterLength() {
        String testObjective = "Verify POST /users fails with 422 when name exceeds maximum character length";
        ExtentTestManager.logInfo("Starting test: " + testObjective);

        String longName = "ThisNameIsWayTooLongAndExceedsTheMaximumAllowedCharacterLimitDefinedByApi";
        String payload = String.format("{ \"name\": \"%s\", \"email\": \"test@example.com\" }", longName);

        ExtentTestManager.logInfo("Sending POST request to '/users' with a name exceeding the maximum character length.");
        Response response = RestAssured
                .given()
                .header("Content-Type", "application/json")
                .body(payload)
                .when()
                .post("/users")
                .then()
                .extract()
                .response();

        ExtentTestManager.logInfo("Verifying status code is 422.");
        Assert.assertEquals(response.getStatusCode(), 422, "Expected status code 422");

        String responseBody = response.getBody().asString();
        ExtentTestManager.logInfo("Verifying error message for exceeding character limit in 'name'.");
        Assert.assertTrue(responseBody.contains("name exceeds the maximum allowed character limit"),
                "Expected error for exceeding character limit in 'name'.");

        ExtentTestManager.logPass("Test passed successfully");
    }

    @Test
    public void verifyPostUsersFailsWith422WhenEmailExceedsMaxCharacterLength() {
        String testObjective = "Verify POST /users fails with 422 when email exceeds maximum character length";
        ExtentTestManager.logInfo("Starting test: " + testObjective);

        String longEmail = "averylongemailaddresswhichexceedsthemaximumcharacterlimit@example.com";
        String payload = String.format("{ \"name\": \"John Doe\", \"email\": \"%s\" }", longEmail);

        ExtentTestManager.logInfo("Sending POST request to '/users' with an email exceeding the maximum character length.");
        Response response = RestAssured
                .given()
                .header("Content-Type", "application/json")
                .body(payload)
                .when()
                .post("/users")
                .then()
                .extract()
                .response();

        ExtentTestManager.logInfo("Verifying status code is 422.");
        Assert.assertEquals(response.getStatusCode(), 422, "Expected status code 422");

        String responseBody = response.getBody().asString();
        ExtentTestManager.logInfo("Verifying error message for exceeding character limit in 'email'.");
        Assert.assertTrue(responseBody.contains("email exceeds the maximum allowed character limit"),
                "Expected error for exceeding character limit in 'email'.");

        ExtentTestManager.logPass("Test passed successfully");
    }

    // Add additional tests following the same pattern for other test cases.
}