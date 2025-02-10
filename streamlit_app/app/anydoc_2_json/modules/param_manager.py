# app/anydoc_2_json/modules/param_manager.py

import os
import yaml

class ParamManager:
    """
    ParamManager class for managing parameter configuration, loading from and saving to YAML files,
    providing access to parameter values, setting default values, and validating parameters as per program requirements.

    Dependencies:
        - Built-in `os` module for file system interactions.
        - `yaml` module for parsing YAML files. Requires PyYAML package (ensure it's installed in your environment).

    Upstream functions:
        - Any function or module in the system that requires access to parameters should use this class.

    Downstream functions:
        - `load_parameters`
        - `save_parameters`
        - `get_parameter`
        - `set_parameter`
        - `validate_parameters`
        - `update_parameters`
        - `parameter_exists`

    """

    def __init__(self, param_file_path: str = None):
        """
        Initialize the ParamManager instance.

        Parameters:
            param_file_path (str, optional):
                The full path to the parameter YAML file. Defaults to None.

        Returns:
            None

        Raises:
            FileNotFoundError:
                If the parameter file does not exist at the specified path.
            PermissionError:
                If the program lacks permissions to read the parameter file.
            yaml.YAMLError:
                If the parameter file contains invalid YAML syntax.

        Dependencies:
            - `os.path.exists` to check if the file exists.
            - `self.load_parameters` to load parameters from the file.

        Upstream functions:
            - Constructor called by modules requiring parameter access.

        Downstream functions:
            - `load_parameters`

        """
        self.parameters = {}
        self.param_file_path = param_file_path

        if self.param_file_path:
            if not os.path.exists(self.param_file_path):
                raise FileNotFoundError(f"Parameter file not found: '{self.param_file_path}'")
            self.load_parameters(self.param_file_path)

    def load_parameters(self, param_file_path: str):
        """
        Load parameters from a YAML file.

        Parameters:
            param_file_path (str):
                The path to the YAML file containing parameters.

        Returns:
            None

        Raises:
            FileNotFoundError:
                If the parameter file does not exist.
            PermissionError:
                If the program lacks permissions to read the parameter file.
            yaml.YAMLError:
                If the YAML file contains invalid syntax.

        Dependencies:
            - `open` to read the file.
            - `yaml.safe_load` to parse YAML content.

        Upstream functions:
            - `__init__`
            - Functions needing to reload parameters from a file.

        Downstream functions:
            - None

        """
        if not os.path.exists(param_file_path):
            raise FileNotFoundError(f"Parameter file not found: '{param_file_path}'")

        try:
            with open(param_file_path, 'r', encoding='utf-8') as file:
                self.parameters = yaml.safe_load(file) or {}
                self.param_file_path = param_file_path
            # Remove 'target' parameter if it exists
            self.parameters.pop('target', None)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file '{param_file_path}': {e}")
        except Exception as e:
            raise IOError(f"Failed to read parameter file '{param_file_path}': {e}")

    def save_parameters(self, param_file_path: str = None):
        """
        Save parameters to a YAML file.

        Parameters:
            param_file_path (str, optional):
                The path to the YAML file where parameters will be saved. If None, saves to the original file path.

        Returns:
            None

        Raises:
            IOError:
                If the parameter file cannot be written.
            yaml.YAMLError:
                If there is an error during YAML serialization.

        Dependencies:
            - `open` to write the file.
            - `yaml.safe_dump` to serialize parameters to YAML.

        Upstream functions:
            - Functions that update parameters and need to save them.

        Downstream functions:
            - None

        """
        if not param_file_path:
            if not self.param_file_path:
                raise ValueError("No parameter file path specified to save parameters.")
            param_file_path = self.param_file_path
        # Remove 'target' parameter if it exists
        self.parameters.pop('target', None)
        try:
            with open(param_file_path, 'w', encoding='utf-8') as file:
                yaml.safe_dump(self.parameters, file)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error serializing parameters to YAML: {e}")
        except Exception as e:
            raise IOError(f"Failed to write parameter file '{param_file_path}': {e}")

    def get_parameter(self, key: str, default=None):
        """
        Get the value of a parameter by key.

        Parameters:
            key (str):
                The key of the parameter to retrieve.
            default (optional):
                The default value to return if the key is not found. Defaults to None.

        Returns:
            The value of the parameter if found; otherwise, the default value.

        Raises:
            None

        Dependencies:
            - Accesses `self.parameters` dictionary.

        Upstream functions:
            - Any function needing to retrieve a parameter value.

        Downstream functions:
            - None

        """
        return self.parameters.get(key, default)

    def set_parameter(self, key: str, value):
        """
        Set the value of a parameter.

        Parameters:
            key (str):
                The key of the parameter to set.
            value:
                The value to set for the parameter.

        Returns:
            None

        Raises:
            None

        Dependencies:
            - Modifies `self.parameters` dictionary.

        Upstream functions:
            - Any function needing to set or update a parameter value.

        Downstream functions:
            - None

        """
        self.parameters[key] = value

    def validate_parameters(self):
        """
        Validate the parameters, ensuring required parameters are present and valid.

        Parameters:
            None

        Returns:
            None

        Raises:
            ValueError:
                If required parameters are missing or invalid.

        Dependencies:
            - Checks `self.parameters` dictionary.

        Upstream functions:
            - Functions that need to ensure parameters are valid before proceeding.

        Downstream functions:
            - None

        """

        # Validate 'replaceFormControls'
        replace_form_controls = self.parameters.get('replaceFormControls', 'yes')
        if replace_form_controls not in ['yes', 'no']:
            raise ValueError("Parameter 'replaceFormControls' must be 'yes' or 'no'.")

        # Validate 'removeTexts' structure
        remove_texts = self.parameters.get('removeTexts', [])
        if remove_texts:
            if not isinstance(remove_texts, list):
                raise ValueError("Parameter 'removeTexts' must be a list of dictionaries.")
            for rule in remove_texts:
                if not isinstance(rule, dict):
                    raise ValueError("Each removal rule in 'removeTexts' must be a dictionary.")
                if 'start' not in rule or 'end' not in rule:
                    raise ValueError("Each removal rule must have 'start' and 'end' keys.")

        # Validate 'replaceText' structure
        replace_text = self.parameters.get('replaceText', [])
        if replace_text:
            if not isinstance(replace_text, list):
                raise ValueError("Parameter 'replaceText' must be a list of dictionaries.")
            for rule in replace_text:
                if not isinstance(rule, dict):
                    raise ValueError("Each replacement rule in 'replaceText' must be a dictionary.")
                if 'from' not in rule or 'to' not in rule:
                    raise ValueError("Each replacement rule must have 'from' and 'to' keys.")

        # Validate 'anonymization' structure
        anonymization = self.parameters.get('anonymization', {})
        if anonymization:
            valid_categories = ['email', 'person name', 'organization']
            valid_methods = ['redact', 'jibberish', 'realistic']
            if not isinstance(anonymization, dict):
                raise ValueError("Parameter 'anonymization' must be a dictionary.")
            for category, method in anonymization.items():
                if category not in valid_categories:
                    raise ValueError(f"Invalid category '{category}' in 'anonymization'.")
                if method not in valid_methods:
                    raise ValueError(f"Invalid method '{method}' for category '{category}' in 'anonymization'.")

        # Validate 'adjustDates' structure
        adjust_dates = self.parameters.get('adjustDates', {})
        if adjust_dates:
            valid_keys = ['add', 'subtract', 'daysBefore', 'daysAfter']
            if not isinstance(adjust_dates, dict):
                raise ValueError("Parameter 'adjustDates' must be a dictionary.")
            for key, value in adjust_dates.items():
                if key not in valid_keys:
                    raise ValueError(f"Invalid key '{key}' in 'adjustDates'.")
                if not isinstance(value, int) or value <= 0:
                    raise ValueError(f"Value for '{key}' in 'adjustDates' must be an integer greater than 0.")

        # Validate 'removeEmptyRows'
        remove_empty_rows = self.parameters.get('removeEmptyRows', 'yes')
        if remove_empty_rows not in ['yes', 'no']:
            raise ValueError("Parameter 'removeEmptyRows' must be 'yes' or 'no'.")

        # Validate 'removeRowsWithString'
        remove_rows_with_string = self.parameters.get('removeRowsWithString', '')

        # Validate 'removeEmptyColumns'
        remove_empty_columns = self.parameters.get('removeEmptyColumns', 'yes')
        if remove_empty_columns not in ['yes', 'no']:
            raise ValueError("Parameter 'removeEmptyColumns' must be 'yes' or 'no'.")

        # Validate '2pass_cleanup'
        two_pass_cleanup = self.parameters.get('2pass_cleanup', 'no')
        if two_pass_cleanup not in ['yes', 'no']:
            raise ValueError("Parameter '2pass_cleanup' must be 'yes' or 'no'.")
            
    def update_parameters(self, params: dict, overwrite: bool = True):
        """
        Update parameters with a dictionary of new values.

        Parameters:
            params (dict):
                A dictionary containing parameter keys and values to update.
            overwrite (bool, optional):
                If True, existing parameters will be overwritten with new values.
                If False, existing parameters will not be overwritten. Defaults to True.

        Returns:
            None

        Raises:
            TypeError:
                If 'params' is not a dictionary.

        Dependencies:
            - Modifies `self.parameters` dictionary.

        Upstream functions:
            - Functions that need to update multiple parameters at once.

        Downstream functions:
            - None

        """
        if not isinstance(params, dict):
            raise TypeError("Parameter 'params' must be a dictionary.")
        for key, value in params.items():
            if overwrite or key not in self.parameters:
                self.parameters[key] = value

    def parameter_exists(self, key: str) -> bool:
        """
        Check if a parameter exists.

        Parameters:
            key (str):
                The key of the parameter to check.

        Returns:
            bool:
                True if the parameter exists; False otherwise.

        Raises:
            None

        Dependencies:
            - Accesses `self.parameters` dictionary.

        Upstream functions:
            - Functions that need to check for parameter existence before proceeding.

        Downstream functions:
            - None

        """
        return key in self.parameters