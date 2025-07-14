import abc


class BaseCommandHandler(abc.ABC):
    """
    Base class for command handlers.
    """

    command_name: str = "{command_name}"
    command_description: str = "{command_description}"

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        """
        Method to handle the command.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result of the command execution.
        """
        pass
