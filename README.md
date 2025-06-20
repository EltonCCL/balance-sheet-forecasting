# balance-sheet-forecasting

This project provides tools to download, analyze, and forecast financial statements for a given company ticker.

## File Structure

```
.
├── config/
│   └── MSFT/
│       ├── balance_sheet_map.json
│       ├── cash_flow_map.json
│       └── income_statement_map.json
├── company_fs.py
├── example.ipynb
├── README.md
├── requirements.txt
├── quick_notes.md
├── forecasting.pdf
└── utils.py
```

- `company_fs.py`: Contains the `CompanyFS` class, which handles fetching data from Yahoo Finance, parsing financial statements, and running forecasts.
- `utils.py`: Utility functions used by other scripts.
- `config/`: Contains configuration files for mapping financial statement items. Each subdirectory is named after a stock ticker (e.g., `MSFT`).
- `requirements.txt`: A list of python dependencies for the project.
- `*.ipynb`: Jupyter notebooks for testing and experimentation.
- `quick_notes.md`: Notes on this topic.
- `forecasting.pdf`: Wrap up of this work.

## Usage

1. **Install dependencies:**

   Open a terminal and run the following command to install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Please check `example.ipynb`