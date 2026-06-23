"""
Service for parsing extracted data.
"""
import re
from typing import List
from dataclasses import dataclass
from utils.logger import logger

@dataclass
class NayaPyneBlock:
    """Structured object representing a parsed data block."""
    ch_value: str
    off_values: List[str]
    rl_values: List[str]

class DataParser:
    """
    Class responsible for parsing raw data extracted from PDF.
    Uses boundary heuristics to overcome right-to-left string reversal 
    and heavily fragmented layouts in AutoCAD PDFs.
    """
    def __init__(self):
        logger.info("Initializing DataParser")

    def parse_data(self, raw_data: str) -> List[NayaPyneBlock]:
        logger.debug("Parsing extracted data")
        if not raw_data:
            logger.warning("No raw data provided for parsing.")
            return []

        parsed_blocks = []
        pages = raw_data.split("---PAGE_BREAK---")
        logger.info(f"Document split into {len(pages)} pages for parsing.")

        title_pattern = re.compile(r"([^:\r\n]+):+\s*([\d\.]+)")
        float_pattern = re.compile(r"-?\d+\.\d+-?|\d+-?")

        for page_idx, page_text in enumerate(pages):
            # 1. Extract titles
            titles = []
            for match in title_pattern.finditer(page_text):
                name_part = match.group(1).strip().lower()
                val_str = match.group(2).strip()
                
                def try_undouble(s: str) -> str:
                    if len(s) > 0 and len(s) % 2 == 0:
                        if all(s[i] == s[i+1] for i in range(0, len(s), 2)):
                            return s[0::2]
                    return s
                    
                name_part_undoubled = try_undouble(name_part)
                val_str_undoubled = try_undouble(val_str)
                
                if "datum" not in name_part_undoubled and "area" not in name_part_undoubled:
                    titles.append(val_str_undoubled)
                    
            N = len(titles)
            if N == 0:
                continue

            # 2. Find region boundaries
            markers = []
            for m in re.finditer(r"PRE[\s\S]{0,10}OFF", page_text): markers.append((m.start(), "PRE_OFF", m.end()))
            for m in re.finditer(r"PRE[\s\S]{0,10}RL", page_text): markers.append((m.start(), "PRE_RL", m.end()))
            for m in re.finditer(r"POST[\s\S]{0,10}OFF", page_text): markers.append((m.start(), "POST_OFF", m.end()))
            for m in re.finditer(r"POST[\s\S]{0,10}RL", page_text): markers.append((m.start(), "POST_RL", m.end()))
            for m in title_pattern.finditer(page_text): markers.append((m.start(), "TITLE_OR_DATUM", m.end()))
            for m in re.finditer(r"AREA", page_text, re.IGNORECASE): markers.append((m.start(), "AREA", m.end()))
            for m in re.finditer(r"Datum", page_text, re.IGNORECASE): markers.append((m.start(), "DATUM", m.end()))
            
            markers.sort(key=lambda x: x[0])
            
            post_off_regions = []
            post_rl_regions = []
            
            for i in range(len(markers)):
                start_idx = markers[i][2]
                end_idx = markers[i+1][0] if i+1 < len(markers) else len(page_text)
                
                region_type = markers[i][1]
                region_text = page_text[start_idx:end_idx]
                
                if region_type == "POST_OFF":
                    post_off_regions.append(float_pattern.findall(region_text))
                elif region_type == "POST_RL":
                    post_rl_regions.append(float_pattern.findall(region_text))
                    
            if not post_off_regions or not post_rl_regions:
                logger.warning(f"Page {page_idx + 1}: Missing POST regions. Skipping.")
                continue
                
            all_post_off = []
            all_post_rl = []
            
            # Combine regions securely based on block graph sizes
            if len(post_off_regions) == len(post_rl_regions):
                for off_floats, rl_floats in zip(post_off_regions, post_rl_regions):
                    k_graphs = len(off_floats) // 5
                    all_post_off.extend(off_floats[:k_graphs * 5])
                    all_post_rl.extend(rl_floats[:k_graphs * 5])
            else:
                logger.warning(f"Page {page_idx + 1}: Mismatched region pairs. Fallback to raw concatenation.")
                for off_floats in post_off_regions: all_post_off.extend(off_floats)
                for rl_floats in post_rl_regions: all_post_rl.extend(rl_floats)
            
            def reverse_string(s: str) -> str:
                return s[::-1]
                
            post_off_reversed = [reverse_string(f) for f in all_post_off]
            post_rl_reversed = [reverse_string(f) for f in all_post_rl]
            
            expected_count = 5 * N
            
            if len(post_off_reversed) != expected_count:
                logger.warning(f"Page {page_idx + 1}: Expected {expected_count} POST OFF floats, found {len(post_off_reversed)}")
            if len(post_rl_reversed) != expected_count:
                logger.warning(f"Page {page_idx + 1}: Expected {expected_count} POST RL floats, found {len(post_rl_reversed)}")
                
            # Chunk into blocks of 5
            off_chunks = [post_off_reversed[i:i+5] for i in range(0, len(post_off_reversed), 5)]
            rl_chunks = [post_rl_reversed[i:i+5] for i in range(0, len(post_rl_reversed), 5)]
            
            # Assemble blocks safely
            for i in range(min(N, len(off_chunks), len(rl_chunks))):
                parsed_blocks.append(
                    NayaPyneBlock(
                        ch_value=titles[i],
                        off_values=off_chunks[i],
                        rl_values=rl_chunks[i]
                    )
                )

        if not parsed_blocks:
            raise ValueError("No valid graph blocks found in the document.")
            
        try:
            parsed_blocks.sort(key=lambda block: float(block.ch_value))
            logger.info("Successfully sorted graph blocks by CH value in increasing order.")
        except Exception as e:
            logger.warning(f"Failed to sort blocks by CH value: {e}")
            
        logger.info(f"Successfully assembled {len(parsed_blocks)} NayaPyneBlocks.")
        return parsed_blocks
