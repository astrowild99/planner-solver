# Integration tests

Integration tests will be run only with the full stack described in [the test compose file](../../compose.test.yaml)

## Configs

The configs used for testing purposes are in the configs folder, and are mounted in the docker compose

## Dir mapping

Beware! integration tests can **only** be run with docker as they strongly depend on the docker container filesystem