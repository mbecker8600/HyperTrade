"""main_tests.py: Test what logging will look like running in an actual program.

This is just a manual test to see what the logging will look like when running the program without running unit tests. 
It is purely manual at this point and meant more for debugging issues with logging than anything else.

"""

from loguru import logger
from hypertrade.libs.logging.setup import initialize_logging

# Debug testing
# import debugpy
# debugpy.listen(5678)
# debugpy.wait_for_client()


if __name__ == "__main__":
    """Main function to test logging setup.

    This function will setup the logging for the project and then log a message to the console.

    Usage:
        bazel run //hypertrade/libs/logging/tests:main_tests

    """

    initialize_logging()
    logger.info("Logging setup complete")
