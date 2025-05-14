# Jitsi Slack Bolt - Jitsi Meet Integration for Slack

This is a slack bolt python bolt that provides the backend for a /jitsi bot on your Slack workspace
to easily invite members to video conferences. It is the service run in support of the TBD LINK app
in the Slack Marketplace.

Enables starting and joining [Jitsi Meet](https://meet.jit.si) meetings from within
[Slack](https://slack.com/) channels and direct messages. It's also possible to configure a
custom URL for your workspace and use that instead.

This is a drop-in replacement for [jitsi-slack](https://github.com/jitsi/jitsi/slack)
which is now deprecated because it does not support all modern Slack standards.

## Supported slash commands

* `/jitsi` creates a Jitsi room with a random name
* `/jitsi server` shows the current server configuration for the workspace
* `/jitsi server default` resets server to default - `JITSI_DEFAULT_SERVER`
* `/jitsi server <url>` : Sets custom default server URL for the workspace
* `/jitsi @<user1> .. @<userN>` ceates a Jitsi room and sends it via DM

## Local Development

### Slack

This project is based on the Slack's Bolt library for Python which has an
[excellent getting started guide](https://tools.slack.dev/bolt-python/getting-started/)

To run your own version of this service, you will need to follow the guide to set up your own Slack
app. We recommend you begin in socket mode for development since it is easy to step on your own foot
with OAUTH.

### Python

This is a [python3](https://python.org) project which, leverages the
[Slack python sdk](https://tools.slack.dev/python-slack-sdk/) and the
[Slack bolt sdk](https://tools.slack.dev/bolt-python/).

Service endpoints are handled by [flask](https://flask.palletsprojects.com/en/stable/)
and run within the [gunicorn](https://gunicorn.org) wsgi server.

Current development uses python 3.12.10. There is no support for python 2.

Dependency management uses [poetry](https://python-poetry.org); use `poetry install` to install
all required libraries for development.

### Configuration

The following environment variables configure the service:

#### general

* `JITSI_DEFAULT_SERVER`: the base URL for the server, e.g., `https://meet.jit.si/`
* `SLACK_EVENTS_API_MODE`: Set to "socket" for socket mode, otherwise uses "oauth" and the Events API
* `SLACK_SLASH_CMD`: The slash command to call the service in Slack (defaults to /jitsi)
* `STORAGE_PROVIDER`: "memory", "vault", or "postgres"
* `PORT`: port that gunicorn listens on (default: 3000)
* `PROXY_MODE`: the app is running behind a proxy
* `DEBUG_LEVEL`: error, warn, info, or debug (default: info)

#### socket mode

* `SLACK_BOT_TOKEN`: The bot token for your Slack app (required)
* `SLACK_APP_TOKEN`: The app-level token for your Slack app (required for socket mode)

#### OAUTH mode

* `SLACK_SIGNING_SECRET`: The signing secret for your Slack app
* `SLACK_CLIENT_ID`: OAuth client ID
* `SLACK_CLIENT_SECRET`: OAuth client secret

#### data store configuration - vault

* `VAULT_URL`: URL for vajdult server
* `VAULT_TOKEN`: token for vault access
* `VAULT_MOUNT_POINT`: mount point for secrets
* `VAULT_PATH_PREFIX`: prefix for jitsi-slack k-v store

#### data store configuration - postgres

* `DB_HOST`: postgres host
* `DB_PORT`: port for postgres db
* `DB_USERNAME`: postgres username
* `DB_PASSWORD`: postgres user password
* `DB_NAME`: name of the database

## Running Locally

You can easily perform local development in socket mode.

```bash
'eval $(poetry env activate)'
SLACK_EVENTS_API_MODE="socket" SLACK_BOT_TOKEN=<bot token> SLACK_APP_TOKEN=<app token> poetry run ./start.sh
```

Deploy a container for integration testing.

## Building

The `build.sh` script handles building a container.

## TODO

There is some work to do to make postgres connections work properly if more than one gunicorn worker
is used.

## License

This project is licensed under the Apache 2.0 License [LICENSE](LICENSE)
