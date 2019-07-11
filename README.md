# Reteto - Rest Test Tool

Reteto is a gold copy compare and schema validation tool for REST APIs. It is stack-agnostic, and does not rely on any features of the API.

## Using Reteto
Reteto operates against a yaml document. This document obeys the following structure

```
verbose: false # optional boolean indicating how verbose the tests should be
env: # optional set of environment variables for the test run. These can be nested and of any type
    api: jsonplaceholder.typicode.com # I have nothing to do with jsonplaceholder, it's just a fantastic resource
    ...
suite:
    anyTestName:
        anyExchangeName:
            request:
                method: POST
                target: /posts
                schema: 
                    type: object    # a valid json schema
                    ...
                headers:
                    host: ${env.api}   # a host header is always required
                    content-type: application/json
                    ...
                body:
                    title: foo
                    ...
            response:
                schema:
                    type: object   # a valid json schema
                    ...
                headers: # regular expressions for non-deterministic headers
                    date: /..., \d\d \w+ \d\d\d\d \d\d:\d\d:\d\d GMT/
                    ...
                body: # regular expressions for non-deterministic body values
                    unixTimestamp: /\d+/
                    ...
        anyOtherExchange:
        ...
    anyOtherTest:
    ...
```

### !include directive
To make life a little easier, the yaml parser supports an `!include` directive.

```
suite:
    anyTest: !include test/anyTest.yaml
    otherTest: !include test/otherTest.yaml
```

The `!include` directive can be used at any level. It blindly inserts the document in place.

### Variable expansion
Individual values are rendered against Python's `string.Template`, using the context of past exchanges within a test joined with the `env` content. So in the above example, `${env.api}` would be replaced with `jsonplaceholder.typicode.com` at runtime. This can also be used with past responses.

```
suite:
    authPost:
        auth:
            request:
                method: POST
                target: /auth
                ...
            response:
                body:
                    authToken: /.*/
        post:
            request:
                method: POST
                target: /posts
                headers:
                    authorization: Bearer ${auth.response.body.authToken}
                ...
```

The context resets to just the `env` with each test. Past request/responses are only available within a test context.

### Testing process

currently the verbose output displays the following sequence.

```
create request              # the request data was parsed
log request                 # the request data was logged
validate request            # the request data was validated against the schema
PASS request valid          # the request passed schema validation
send request                # the request data was sent to the API, and the response received
log response                # the response was logged
validate response           # the response was validated against the schema
PASS response valid         # the response passed schema validation
normalize response          # the response was normalized
log actual                  # the normalized (actual) response was logged
load expected               # the expected response was parsed
log expect                  # the expected response was logged
compare actual to expected  # the expected and normalized response were compared
PASS actual match           # the normalized response matched the expected response
```

If `verbose` is `false` or omitted, the output will instead look like `...+...+.....+` where the `.` indicates a step completed, a `+` indicates a check passed, a `-` indicates a check failed, and a `X` indicates an error.

### Test output

The `target` directory will contain the following after the run
```
target/
    actual/     # the normalized responses organized into folders by the test name
        someTest/
            0001.someExchange.response
        ...
    expect/     # the expected responses organized into folders by the test name
        someTest/
            0001.someExchange.response
        ...
    log/        # the raw request/responses organized into folders by the test name
        someTest/
            0001.someExchange.request
            0001.someExchange.response
        ...
    reteto.log  # the test exhuast from the last run
```

### Local development
A `./build` script has been provided for local development testing. It can take an optional argument.
```
clean - remove the target directory
build - build the docker image locally
test - test the docker image locally
update - replace the full gold copy with the latest run
all - run a clean-build-test chain
```
Executing `./build` alone is equivalent to `./build all`.
