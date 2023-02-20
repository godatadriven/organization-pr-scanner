# organization-pr-scanner

![CI](https://github.com/jochemloedeman/organization-pr-tool/actions/workflows/ci.yml/badge.svg
)

Azure Functions app for scraping pull request, user and project data for all members of a (Xebia) GitHub organization. The resulting dataset is used for a set of features:

* A Slack message informing others when new pull requests are detected.
* A (monthly) tabular report which lists some elementary information about the pull requests of the past period.

## Setup
