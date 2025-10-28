# Source Jubelio

This is the repository for the Jubelio source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/jubelio).

## Local development

### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.10`

#### Build & Activate Virtual Environment and install dependencies
From this connector directory, create a virtual environment:
```
python -m venv .venv
```

This will create a new Python virtual environment in the `.venv` directory. To use this environment, you'll need to activate it. To activate it:
```
source .venv/bin/activate
```

Alternatively, you can install and activate using poetry:
```
poetry install
poetry shell
```

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/jubelio)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `src/source_jubelio/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source jubelio test creds`
and place them into `secrets/config.json`.

### Locally running the connector
```
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Locally running the connector docker image

#### Build
First, make sure you build the latest Docker image:
```
docker build . -t airbyte/source-jubelio:dev
```

You can also build the connector image via Airbyte CI:
```
airbyte-ci connectors --name=source-jubelio build
```

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-jubelio:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-jubelio:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-jubelio:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-jubelio:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing
Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.
First install test dependencies into your virtual environment:
```
pip install .[tests]
```

### Unit Tests
To run unit tests locally, from the connector directory run:
```
python -m pytest unit_tests
```

### Integration Tests
There are two types of integration tests: Acceptance Tests (Airbyte's test suite for all source connectors) and custom integration tests (which are specific to this connector).
#### Custom Integration tests
Place custom tests inside `integration_tests/` folder, then, from the connector directory, run
```
python -m pytest integration_tests
```
#### Acceptance Tests
Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.
To run your integration tests with acceptance tests, from the connector directory, run
```
python -m pytest integration_tests -p integration_tests.acceptance
```
To run your integration tests with docker

### Using airbyte-ci
You can also use `airbyte-ci` to test the connector:
```
airbyte-ci connectors --name=source-jubelio test
```

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.
We split dependencies between two groups, dependencies that are:
* required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
* required for the testing need to go to `TEST_REQUIREMENTS` list

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-jubelio test`
2. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
3. Make sure the `metadata.yaml` content is up to date.
4. Make the connector documentation and its changelog is up to date (`docs/integrations/sources/jubelio.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.