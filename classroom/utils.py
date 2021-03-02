import logging

LOGGER = logging.getLogger(__name__)


class NotConnectedToOpenEdX(Exception):
    """
    Exception to raise when not connected to OpenEdX.

    In general, this excepton shouldn't be raised, because this package is
    designed to be installed directly inside an existing OpenEdX platform.
    """

    def __init__(self, *args: object) -> None:
        """
        Log a warning and initialize the exception.
        """
        LOGGER.warning(
            "dt-classroom unexpectedly failed as if not install in an OpenEdX platform"
        )
        super().__init__(*args)