### Quickfix

Electronic repair shop

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app quickfix
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/quickfix
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### Contribution Files Explanation

site_config.json is used for site-specific settings like database credentials and developer mode, whereas common_site_config.json stores global configurations shared across all sites in the bench like the database host. If a secret is accidentally placed in common_site_config.json, it becomes accessible to every site on that bench regardless of its environment. This creates a security risk where production sites might unintentionally leak sensitive data or inherit development-only credentials. Therefore, keeping secrets in the individual site_config.json ensures proper isolation and security for multi-tenant setups.

### Bench Processes
The bench start command launches the following four processes:

web: The web server handling browser requests.

worker: Executes background tasks and asynchronous jobs.

scheduler: Enqueues scheduled events and periodic tasks.

socketio: Provides real-time communication for notifications and updates.

### Background Jobs Impact:
If the worker process crashes, background jobs will remain in the "Queued" state in the database. No background tasks—such as sending emails or processing long reports—will be executed until the worker is restarted.

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
