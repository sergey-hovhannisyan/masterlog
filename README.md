# MasterLog

## This module provides a versatile logging system with configurable log levels, sources, and formatting options. It supports colorized output for terminal logging and allows for file-based logging with customizable settings.

![Terminal Output Example](https://github.com/sergey-hovhannisyan/masterlog/blob/main/docs/output.png?raw=true)

## Features

- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL, RELEASE
- **Source-Based Filtering:** Log messages can be filtered by source, with optional colorization.
- **Customizable Format:** Adjust log message format and date format.
- **File Logging:** Option to save logs to a file with configurable filename.
- **Dynamic Source Management:** Add or remove logging sources and set a default source.

## Installation

You can install MasterLog directly from PyPI:
```bash
pip install --upgrade
pip install masterlog
```

Alternatively, you can clone the repository (no external dependencies required):
```bash
git clone https://github.com/sergey-hovhannisyan/masterlog.git
```

## Usage

- **Configure the logger** using the `config` function.
- **Log messages** at various levels using `debug`, `info`, `warning`, `error`, and `critical`.
- **Manage logging sources** with `add_source` and `remove_source`.
- **Toggle logging** with `enable` and `disable`.
- **Set or update the default logging source** with `set_default_source`.

## Examples

```python
import masterlog as log

log.config(level=log.DEBUG, sources=('SYSTEM', 'APP'), format="{asctime} {source} - {levelname}: {message}")
log.info("This is an info message", source="APP")
log.error("This is an error message", source="SYSTEM")
```

### Configuration

Configure the logger using the `config` function:

```python
# Basic configuration
log.config(level=log.DEBUG, sources=('SYSTEM', 'APP'), format="{asctime} {source} - {levelname}: {message}")

# Enable file logging
log.config(enable_save=True, filename="output.log")
```

### Logging Messages
Log messages at various levels:

```python
log.info("This is an info message", source="APP")
log.error("This is an error message", source="SYSTEM")
log.critical("Critical system failure detected.")
log.warning("Disk space running low.")
```
### Source Management
Manage logging sources:
```python
log.add_source("DATABASE", "MAGENTA")
log.add_source("API", "GREEN")
log.remove_source("SYSTEM")
```

### Dynamic Source and Logging Control
Switch between terminal and file outputs, and adjust logging levels and sources:

```python
# Switch to terminal output only
log.config(enable_save=False)
log.info("Application server started on port 8080.", source="SERVER")
log.warning("User session timeout approaching.", source="SESSION")
```
```python
# Add and remove sources
log.add_source("DATABASE", "MAGENTA")
log.add_source("API", "GREEN")

log.info("API key successfully refreshed.", source="API")
log.debug("Database query execution time: 120ms.", source="DATABASE")

log.remove_source("SYSTEM")
log.info("The 'SYSTEM' source was deleted. Printing from the default source.")
```
```python
# Log level control
log.disable()
log.info("This will not be logged!")
log.enable()
log.critical("Critical error in authentication service: key rotation failed.", source="AUTH")
```
```python
# Configure sources and default source
log.config(sources=("SYSTEM", "API"))
log.error("This will not be logged!", source="FILESYSTEM")
log.warning("API response took longer than expected: 2 seconds.", source="API")

log.set_default_source("SERVICE")
log.info("Hello from service.")

log.set_default_source("NETWORK", "YELLOW")
log.debug("Network request payload: {\"user_id\": 123}.")
```

## Shutdown Hook
The masterlog shutdown hook clears the buffer and writes the buffer into the file if enable_save was set before exiting.

## Contributing
Feel free to submit issues and pull requests on GitHub. Contributions are welcome!

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/sergey-hovhannisyan/masterlog/blob/main/LICENSE) file for details.