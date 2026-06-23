"""
Service for generating Excel files.
"""
import os
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
from typing import List, Dict, Any
from utils.logger import logger

class ExcelGenerator:
    """
    Class responsible for creating Excel files from transformed data.
    """
    def __init__(self):
        logger.info("Initializing ExcelGenerator")
        self.headers = ["CH", "OFF", "BS", "IS", "FS", "HI", "RL", "REMARKS"]

    def generate_excel(self, transformed_data: List[Dict[str, Any]], output_path: str) -> str:
        """
        Generates an Excel file from the provided data at the given output path.
        Returns the absolute path of the generated file.
        """
        logger.debug(f"Generating Excel file at: {output_path}")
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Output Data"

            # 1. Add headers
            ws.append(self.headers)

            # 2. Write all rows
            for row_data in transformed_data:
                row = [row_data.get(header, "") for header in self.headers]
                ws.append(row)

            # Define styles
            bold_font = Font(bold=True)
            center_alignment = Alignment(horizontal='center', vertical='center')

            # 3. Format Headers and auto filter
            for col_idx, _ in enumerate(self.headers, start=1):
                cell = ws.cell(row=1, column=col_idx)
                # Header bold
                cell.font = bold_font
                
            # Center alignment for all cells
            for row in ws.iter_rows():
                for cell in row:
                    cell.alignment = center_alignment

            # 4. Auto filter
            last_col_letter = get_column_letter(len(self.headers))
            last_row = ws.max_row
            ws.auto_filter.ref = f"A1:{last_col_letter}{last_row}"

            # 5. Freeze first row
            ws.freeze_panes = 'A2'

            # 6. Set column widths
            for col_idx, header in enumerate(self.headers, start=1):
                col_letter = get_column_letter(col_idx)
                # Set width to a reasonable fixed size
                ws.column_dimensions[col_letter].width = 15

            # 7. Set Page Setup to A4 and Fit to Page width
            ws.page_setup.paperSize = ws.PAPERSIZE_A4
            ws.page_setup.fitToPage = True
            ws.page_setup.fitToWidth = 1
            ws.page_setup.fitToHeight = 0
            ws.sheet_properties.pageSetUpPr.fitToPage = True

            # Save the workbook
            wb.save(output_path)
            logger.info(f"Excel file successfully generated at {output_path}")
            
            return output_path

        except Exception as e:
            logger.error(f"Error generating Excel file: {e}", exc_info=True)
            raise e
