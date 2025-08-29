import logging
import os
import tomllib
from getpass import getpass
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

LOCAL_CONFIG_FILE = Path.home() / ".config/jiruff/config.toml"
if not LOCAL_CONFIG_FILE.exists():
    LOCAL_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_CONFIG_FILE.touch()


class Config(BaseSettings):
    company: str

    jira_url: str | None = None
    jira_user: str | None = None
    jira_token: str | None = None

    gitlab_url: str | None = None
    gitlab_token: str | None = None

    notify: bool = Field(
        default=False,
        description="Whether to notify users about changes made during formatting.",
    )

    raw_config: dict = Field(default_factory=dict)

    def get_config_dict(self, prefix: str) -> dict:
        """
        Get rule configuration dictionary by a specific prefix.
        :param prefix:
        :return:
        """
        for key, value in self.raw_config.items():
            if key.startswith(prefix):
                return self.raw_config.get(key, {})
        return {}


def validate_config_dict(config_dict: dict) -> None:
    """
    Validate the configuration dictionary.

    :param config_dict: Dictionary containing configuration settings.
    :raises ValueError: If required fields are missing or invalid.
    """
    required_fields = ["company"]
    for field in required_fields:
        if field not in config_dict:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(config_dict["company"], str):
        raise ValueError("Field 'company' must be a string.")


def append_jira_auth_info(config: Config):
    """
    Append JIRA authentication information to the configuration.

    :param config: Config object to append JIRA settings.
    """
    if config.jira_url is None:
        logger.info("JIRA URL is not set in the configuration.")
        return

    if config.jira_user is not None and config.jira_token is not None:
        logger.debug("JIRA user and token are already set in the configuration.")
        return

    # first try to load from environment variables
    jira_user_env = os.getenv(f"{config.company.upper()}_JIRA_USER")
    if jira_user_env:
        jira_token_env = os.getenv(f"{config.company.upper()}_JIRA_TOKEN")
        if jira_token_env is None:
            raise ValueError(
                f"JIRA token not found in environment variables for user {jira_user_env}."
            )

        logger.debug(f"Loaded JIRA user from environment: {config.jira_user}")
        config.jira_user = jira_user_env
        config.jira_token = jira_token_env
        return

    # second try to load from local keyring
    try:
        import keyring

        # let's look into LOCAL_CONFIG_FILE for jira user
        if config.jira_user is None:
            if LOCAL_CONFIG_FILE.exists():
                config_dict = tomllib.loads(
                    LOCAL_CONFIG_FILE.read_text(encoding="utf8")
                )
                config.jira_user = config_dict.get(
                    f"{config.company.lower()}_jira_user"
                )

        if config.jira_user is None:
            # let's ask user for jira user
            config.jira_user = input(f"Enter JIRA user for {config.company}: ").strip()
            LOCAL_CONFIG_FILE.write_text(
                data=f"{config.company.lower()}_jira_user = '{config.jira_user}'\n",
                encoding="utf8",
            )

        jira_token_keyring = keyring.get_password(
            service_name=f"{config.company.lower()}-jira", username=config.jira_user
        )
        if jira_token_keyring is not None:
            config.jira_token = jira_token_keyring
            logger.debug(f"Loaded JIRA token from keyring for user {config.jira_user}.")
            return
        else:
            # ask user for jira token
            config.jira_token = getpass(
                f"Enter JIRA token for {config.jira_user}: "
            ).strip()
            keyring.set_password(
                service_name=f"{config.company.lower()}-jira",
                username=config.jira_user,
                password=config.jira_token,
            )
    except ImportError:
        logger.error("Keyring module is not installed. Cannot load JIRA credentials.")

    if config.jira_token is None:
        raise ValueError("JIRA token is not set. Please raise an issue.")


def append_gitlab_auth_info(config: Config):
    """
    Append GitLab authentication information to the configuration.

    :param config: Config object to append GitLab settings.
    """
    if config.gitlab_url is None:
        logger.info("GitLab URL is not set in the configuration.")
        return

    if config.gitlab_token is not None:
        logger.debug("GitLab token is already set in the configuration.")
        return

    # first try to load from environment variables
    gitlab_token_env = os.getenv(f"{config.company.upper()}_GITLAB_TOKEN")
    if gitlab_token_env:
        config.gitlab_token = gitlab_token_env
        logger.debug(f"Loaded GitLab token from environment for {config.company}.")
        return

    # second try to load from local keyring
    try:
        import keyring

        gitlab_token_keyring = keyring.get_password(
            service_name=f"{config.company.lower()}-gitlab", username=config.gitlab_url
        )
        if gitlab_token_keyring is not None:
            config.gitlab_token = gitlab_token_keyring
            logger.debug(f"Loaded GitLab token from keyring for {config.company}.")
            return
        else:
            # ask user for gitlab token
            config.gitlab_token = getpass(
                f"Enter GitLab token for {config.company}: "
            ).strip()
            keyring.set_password(
                service_name=f"{config.company.lower()}-gitlab",
                username=config.gitlab_url,
                password=config.gitlab_token,
            )
    except ImportError:
        logger.error("Keyring module is not installed. Cannot load GitLab credentials.")

    if config.gitlab_token is None:
        raise ValueError("GitLab token is not set. Please raise an issue.")


def load_config(config_path: Path | None = None) -> Config:
    """
    Load configuration from a TOML file.

    :param config_path: Path to the configuration file.
    :return: Config object with loaded settings.
    """
    if config_path is None:
        config_path = LOCAL_CONFIG_FILE

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")

    logger.debug(f"Loading configuration from {config_path}")

    config_dict = tomllib.loads(config_path.read_text(encoding="utf8"))
    validate_config_dict(config_dict)

    config = Config(
        company=config_dict.get("company"),
        jira_url=config_dict.get("jira_url", None),
        gitlab_url=config_dict.get("gitlab_url", None),
    )
    config.raw_config = config_dict
    append_jira_auth_info(config)
    append_gitlab_auth_info(config)
    return config
