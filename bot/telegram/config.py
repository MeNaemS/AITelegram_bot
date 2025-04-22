from dynaconf import Dynaconf
from schemas.settings import Settings

settings: Settings = Dynaconf(
    settings_files=['configs/config.json', 'configs/secret.json'],
    secrets=['configs/secret.json'],
    merge_enabled=True
)
