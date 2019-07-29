class AsteroidTrackerError(Exception):
    """Base class for asteroid-tracker exceptions"""

class TomConnectionError(AsteroidTrackerError):
    """Error connecting to the TOM instance API"""

class InvalidConfigError(AsteroidTrackerError):
    """Config was invalid"""
