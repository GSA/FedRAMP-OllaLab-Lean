# Data Unificator

This application read all data source files from a local folder and properly merge them all into one file.

```
app/
│
├── pages/
│   │
│   ├── data_unificator.py          # Data Unificator app page
│   └── ...
└── data_unificator/
    │
    ├── app.py                      # Main entry point for the Streamlit app
    ├── config.py                   # Configuration management
    ├── requirements.txt            # Required packages
    ├── README.md                   # Documentation
    ├── logs/                       # Logs directory for error, event logs, and audit trails
    ├── tests/                      # Unit and integration tests
    ├── modules/                    # Core logic for each step of the pipeline
    │   └── data_import.py          # Handles data import logic
    │   └── data_mapping.py         # Handles data mapping and conflict resolution
    │   └── data_normalization.py   # Handles data normalization
    │   └── data_deduplication.py   # Handles data deduplication and merging
    │   └── data_validation.py      # Validates data after import and consolidation
    │   └── utils.py                # Common utility functions
    ├── api/                        # API layer to wrap backend functions
    ├── components/                 # Streamlit components and fragments
    │   └── import_ui.py            # GUI for data import
    │   └── mapping_ui.py           # GUI for mapping and conflict resolution
    │   └── normalization_ui.py     # GUI for data normalization
    │   └── deduplication_ui.py     # GUI for data deduplication
    │   └── validation_ui.py        # GUI for data validation and export
    └── utils/                      # Utility functions
        ├── file_utils.py
        ├── logging_utils.py
        ├── security_utils.py
        ├── eda_utils.py
        ├── exception_utils.py
        ├── mapping_utils.py
        ├── normalization_utils.py
        ├── deduplication_utils.py
        └── validation_utils.py
```

More details will soon be added.
