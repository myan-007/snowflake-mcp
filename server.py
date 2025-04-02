import pandas as pd
import xlsxwriter
import os
from typing import Dict,Union


def create_formatted_excel(
    data: Dict[str, pd.DataFrame],
    file_name: str = "financial_report.xlsx",
    location: str = "./reports",
    formatting_config: Dict[str, Union[dict, list]] = None
) -> str:
    """
    Create a professionally formatted Excel file with financial data.
    
    Args:
        data (Dict[str, pd.DataFrame]): Dictionary where keys are sheet names 
               and values are pandas DataFrames
        file_name (str): Output file name (default: financial_report.xlsx)
        location (str): Save directory (default: ./reports)
        formatting_config (Dict): Formatting options containing:
            - headers: Format for header row
            - number_formats: Column-specific number formatting
            - autofit_columns: Whether to auto-adjust column widths
            - conditional_formatting: List of conditional formatting rules
            - sheet_options: Per-sheet formatting configurations
    
    Returns:
        str: File path if successful, error message if failed
    """
    try:
        # Create output directory if needed
        os.makedirs(location, exist_ok=True)
        full_path = os.path.join(location, file_name)

        # Default formatting configuration
        default_formatting = {
            "headers": {
                "bold": True,
                "bg_color": "#4F81BD",
                "font_color": "#FFFFFF",
                "border": 1
            },
            "number_formats": {
                "currency": {"num_format": "$#,##0.00"},
                "percentage": {"num_format": "0.00%"},
                "date": {"num_format": "yyyy-mm-dd"}
            },
            "autofit_columns": True,
            "conditional_formatting": [],
            "sheet_options": {}
        }

        # Merge user config with defaults
        if formatting_config:
            formatting = {**default_formatting, **formatting_config}
        else:
            formatting = default_formatting

        # Create Excel writer object
        with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            header_format = workbook.add_format(formatting["headers"])

            for sheet_name, df in data.items():
                # Write DataFrame to Excel
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                worksheet = writer.sheets[sheet_name]
                
                # Apply header formatting
                worksheet.set_row(0, None, header_format)
                
                # Apply number formatting
                if "number_formats" in formatting:
                    for col_idx, col in enumerate(df.columns):
                        col_type = df[col].dtype
                        if col_type in ['float64', 'int64']:
                            num_format = formatting["number_formats"].get(
                                "currency", {"num_format": "#,##0.00"}
                            )
                            worksheet.set_column(
                                col_idx, col_idx, None, 
                                workbook.add_format(num_format)
                            )
                
                # Auto-fit columns
                if formatting["autofit_columns"]:
                    for idx, col in enumerate(df.columns):
                        max_len = max((
                            df[col].astype(str).map(len).max(),  # Data length
                            len(str(col))  # Header length
                        )) + 2  # Add padding
                        worksheet.set_column(idx, idx, max_len)

                # Apply conditional formatting
                for rule in formatting.get("conditional_formatting", []):
                    worksheet.conditional_format(
                        rule["range"], 
                        rule["options"]
                    )

                # Apply sheet-specific formatting
                sheet_options = formatting["sheet_options"].get(sheet_name, {})
                if "freeze_panes" in sheet_options:
                    worksheet.freeze_panes(*sheet_options["freeze_panes"])
                
                if "add_chart" in sheet_options:
                    chart = workbook.add_chart(sheet_options["add_chart"]["type"])
                    chart.add_series(sheet_options["add_chart"]["series"])
                    worksheet.insert_chart(
                        sheet_options["add_chart"]["position"], 
                        chart
                    )

        return f"Report successfully created at: {full_path}"

    except Exception as e:
        return f"Error creating Excel file: {str(e)}"
    



if __name__ == "__main__":
    sample_config = {
        "headers": {
            "bold": True,
            "bg_color": "#5B9BD5",
            "font_color": "#FFFFFF",
            "border": 1,
            "align": "center"
        },
        "number_formats": {
            "Revenue": {"num_format": "$#,##0.00"},
            "Growth Rate": {"num_format": "0.00%"}
        },
        "conditional_formatting": [
            {
                "range": "B2:B100",
                "options": {
                    "type": "data_bar",
                    "bar_color": "#63C384"
                }
            }
        ],
        "sheet_options": {
            "Financial Summary": {
                "freeze_panes": (1, 0),
                "add_chart": {
                    "type": {"type": "column"},
                    "series": {
                        "name": "Revenue",
                        "categories": "=Financial Summary!$A$2:$A$10",
                        "values": "=Financial Summary!$B$2:$B$10"
                    },
                    "position": "D2"
                }
            }
        }
    }
    # Sample financial data
    income_data = pd.DataFrame({
        "Quarter": ["Q1", "Q2", "Q3", "Q4"],
        "Revenue": [4500000, 5200000, 4800000, 5500000],
        "EPS": [1.25, 1.45, 1.30, 1.60]
    })

    # Generate formatted report
    result = create_formatted_excel(
        data={"Income Statement": income_data},
        file_name="Q4_earnings.xlsx",
        formatting_config=sample_config
    )
    print(result)

