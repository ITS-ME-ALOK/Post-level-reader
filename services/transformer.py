"""
Service for transforming parsed data.
"""
from typing import List, Dict, Any
from services.parser import NayaPyneBlock
from utils.logger import logger

class DataTransformer:
    """
    Class responsible for transforming parsed data into a format suitable for Excel generation.
    """
    def __init__(self):
        logger.info("Initializing DataTransformer")
        # Define the exact reordering mapping requested
        self.mapping_indices = [2, 1, 0, 3, 4]

    def transform_data(self, parsed_blocks: List[NayaPyneBlock]) -> List[Dict[str, Any]]:
        """
        Transforms the parsed blocks into a flat list of dictionary rows for Excel.
        """
        logger.debug("Transforming parsed data")
        
        final_rows = []
        for block in parsed_blocks:
            try:
                # Apply the mapping to OFF and RL values
                ordered_off = self._apply_mapping(block.off_values)
                ordered_rl = self._apply_mapping(block.rl_values)
                
                # The number of rows generated for this block will be based on the mapping length
                num_rows = min(len(ordered_off), len(ordered_rl))
                
                for i in range(num_rows):
                    ch_val_str = block.ch_value
                    try:
                        if float(ch_val_str).is_integer():
                            ch_val_str = str(int(float(ch_val_str)))
                    except ValueError:
                        pass

                    row = {
                        "CH": ch_val_str,
                        "OFF": ordered_off[i],
                        "BS": "",
                        "IS": "",
                        "FS": "",
                        "HI": "",
                        "RL": ordered_rl[i],
                        "REMARKS": ""
                    }
                    final_rows.append(row)
                    
            except Exception as e:
                logger.error(f"Error transforming block CH {block.ch_value}: {e}", exc_info=True)
                
        logger.info(f"Transformed data into {len(final_rows)} rows.")
        return final_rows

    def _apply_mapping(self, values: List[str]) -> List[str]:
        """
        Applies the [2, 1, 0, 3, 4] mapping to a list of values.
        If the list is shorter than expected, missing values are replaced with an empty string.
        """
        mapped = []
        for idx in self.mapping_indices:
            if idx < len(values):
                mapped.append(values[idx])
            else:
                mapped.append("")
                logger.warning(f"Value at index {idx} missing. Padding with empty string.")
        return mapped
