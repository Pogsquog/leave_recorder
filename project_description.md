# Holliday's holiday app

A simple web app for recording / booking leave, for use as a personal project

## Features

* Month view
* Month / Year date picker
* Click and drag to add leave
* Supports half days
* Clear view of total days leave, leave already taken, leave booked, unbooked leave remaining, days left until end of year
* Auth
* Organisations with filterable shared visibiity between people in the org, invite mechanism, push on change to others in org
* Per user configure how much annual leave you have
* Per user leave carryover with configurable max amount
* Per user choice of week start on Sunday or Monday (default)
* Per user choice of year start date with suitable common business calendar choices, default to 1st Jan
* Rest API with per user API key, rate limited to prevent abuse, openapi docs
* Leave types: vacation and sick leave
* i18n support with proper handling of day names, date formats, and translations
* No approval workflow - leave is self-managed

## Non-requirements

* No export or reports feature (accessible via REST API only)
* No approval workflow

## Deployment

* Deploys to MS azure 
* Very low running cost

## CI/CD

* Unit tests for business logic
* Functional / Integration tests using REST API
* Github actions for build / test / lint

## Developer support

* Can run locally using dockerised deployment
* Simple logging using suitable library

## Operations

* Data backup via cloud service as appropriate

## License

AGPL / Commercial

## Sundries

* .gitignore
* .dockerignore
* README.md
* AGENTS.md
