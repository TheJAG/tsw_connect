import os
from dataclasses import dataclass
from typing import Dict, Any, List

import yaml


@dataclass
class DataConfig:
    filename: str
    columns: List[str]

    @staticmethod
    def from_dict(a_dict: Dict[str, Any]) -> "DataConfig":
        return DataConfig(
            filename=a_dict.get("filename"),
            columns=a_dict.get("columns")
        )

class Config:
    def __init__(self, yaml_dict: Dict[str, Any], config_file: str) -> None:
        self.config_file = config_file
        self.data = self.read_data_config(yaml_dict.get("data"))

    @staticmethod
    def load(config_file_path: str = os.path.join(os.getcwd(), "config.yml")) -> Config:
        """
        Loads the configuration file and initializes a Config object with its contents.
        It reads the YAML configuration from the specified path, processes the content,
        and returns an instance of the Config class. The base directory for the operation
        is determined automatically within the function logic.

        :param config_file_path: The optional path to the configuration YAML file. If not
            specified, it defaults to a relative path within the current working directory.
        :type config_file_path: str
        :return: An instance of the Config class populated with configuration data.
        :rtype: Config

        """
        with open(config_file_path) as f:
            content = yaml.safe_load(f)
        return Config(content.get("tsw_connect"), config_file_path)

    @staticmethod
    def read_data_config(data_config_list: Dict[str, Dict[str, Any]]) -> Dict[DataConfig]:
        return {key: DataConfig.from_dict(values) for key, values in data_config_list.items()}

