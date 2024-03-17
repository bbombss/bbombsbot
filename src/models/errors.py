class ApplicationStateError(Exception):
    """Exception raised when the application is not ready to receive a particular instruction in its current state."""

class DatabaseStateError(Exception):
    """Exception raised when the database is not ready to receive a particular instruction in its current state."""