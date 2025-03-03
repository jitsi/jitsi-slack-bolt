# Jitsi Slack Bolt - Jitsi Meet Integration for Slack

This service provides the backend for a /jitsi command on your Slack workspace to easily invite
members to video conferences. It is the service run in support of the TBD LINK app in the Slack Marketplace.

Enables starting and joining [Jitsi Meet](https://meet.jit.si) meetings from within
[Slack](https://slack.com/) channels and direct messages. It's also possible to configure a
custom URL for your workspace and use that instead.

This is a drop-in replacement for [jitsi-slack](https://github.com/jitsi/jitsi/slack)
which is now deprecated because it does not support all modern Slack standards.

## Getting Started

These instructions will get you started with the ability to run the project
on your local machine for development purposes.

### Prerequisites

#### Python

This project was developed using [python](https://python.org),
[pyenv](https://github.com/pyenv/pyenv), and [poetry](https://python-poetry.org)

As of this writing, it expects python 3.12.9. `poetry install` should install
all required libraries.

#### Slack

This project is based on the Slack's Bolt library for Python which has an
[excellent getting started guide](https://tools.slack.dev/bolt-python/getting-started/)

You can follow this guide to set up your own Slack app. We recommend you begin in socket mode for
development since it is easy to punch yourself in the face with OAUTH, especially if you turn
rotation on. Not that we're speaking from experience or anything.

## Configuration

TBR

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
