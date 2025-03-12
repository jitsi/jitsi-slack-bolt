# Jitsi Slack Bolt - Jitsi Meet Integration for Slack

This service provides the backend for a /jitsi command on your Slack workspace to easily invite
members to video conferences. It is the service run in support of the TBD LINK app in the Slack Marketplace.

Enables starting and joining [Jitsi Meet](https://meet.jit.si) meetings from within
[Slack](https://slack.com/) channels and direct messages. It's also possible to configure a
custom URL for your workspace and use that instead.

This is a drop-in replacement for [jitsi-slack](https://github.com/jitsi/jitsi/slack)
which is now deprecated because it does not support all modern Slack standards.

## Local Development

### Slack

This project is based on the Slack's Bolt library for Python which has an
[excellent getting started guide](https://tools.slack.dev/bolt-python/getting-started/)

If you want to run this service, you will need to follow the guide to set up your own Slack app. We
recommend you begin in socket mode for development since it is easy to step on your own foot with
OAUTH.

### Python

This project is mostly in [python](https://python.org), leveraging the
[Slack python sdk](https://tools.slack.dev/python-slack-sdk/) and the
[Slack bolt sdk](https://tools.slack.dev/bolt-python/).

Current development uses python 3.12.9.

We manage dependencies using [poetry](https://python-poetry.org); `poetry install` should install
all required libraries for development.

### Configuration

The following environment variables configure the service:

- `SLACK_BOT_TOKEN`: The bot token for your Slack app (required)
- `SLACK_APP_TOKEN`: The app-level token for your Slack app (required for socket mode)
- `SLACK_SIGNING_SECRET`: The signing secret for your Slack app (required for events API)
- `SLACK_CLIENT_ID`: OAuth client ID (required for OAuth flow)
- `SLACK_CLIENT_SECRET`: OAuth client secret (required for OAuth flow)
- `SLACK_EVENTS_API_MODE`: Set to "socket" for socket mode, otherwise uses events API
- `SLACK_SLASH_CMD`: The slash command to use for the service (defaults to /jitsi)
- `STORAGE_PROVIDER`: memory or vault
- `JITSI_URL`: Base URL for Jitsi Meet instance (defaults to meet.jit.si)
- `VAULT_URL`
- `VAULT_TOKEN`
- `VAULT_MOUNT_POINT`
- `VAULT_PATH_PREFIX`
- `PORT`: Port to listen on (default: 3000)
- `DEBUG`: Set to true for debug logging


## Running

For dev we recommend the use of socket mode:

```
SLACK_EVENTS_API_MODE="socket" SLACK_BOT_TOKEN=<bot token> SLACK_APP_TOKEN=<app token> poetry run ./start.sh
```

For production you should use a container. In this case, `start.sh` expects `SLACK_SIGNING_SECRET`,
`SLACK_CLIENT_ID`, and `SLACK_CLIENT_SECRET` to be set.

## Building

TBR

## License

This project is licensed under the Apache 2.0 License [LICENSE](LICENSE)
