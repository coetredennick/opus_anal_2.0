# file_utils.py
import os
import glob
from typing import List, Dict, Tuple

from data_detector import DataTypeDetector #

class FileUtils:
    @staticmethod
    def auto_discover_files(directory: str) -> Dict[str, List[str]]: #
        discovered_files = {'drops': [], 'gains': [], 'unknown': []}
        if not os.path.isdir(directory):
            return discovered_files

        for filepath in glob.glob(os.path.join(directory, "*.csv")):
            filename = os.path.basename(filepath).lower()
            
            validation_result = DataTypeDetector.validate_csv_structure(filepath) #
            data_type = validation_result['data_type'] #

            if data_type == 'drops': #
                discovered_files['drops'].append(filepath)
            elif data_type == 'gains': #
                discovered_files['gains'].append(filepath)
            else: 
                if 'drop' in filename and 'gain' not in filename:
                    discovered_files['drops'].append(filepath)
                elif 'gain' in filename and 'drop' not in filename:
                    discovered_files['gains'].append(filepath)
                else:
                    discovered_files['unknown'].append(filepath) #
                    
        return discovered_files

    @staticmethod
    def validate_files_in_directory(directory: str) -> List[Tuple[str, dict]]: #
        results = []
        if not os.path.isdir(directory):
            return results 

        for filepath in glob.glob(os.path.join(directory, "*.csv")):
            filename = os.path.basename(filepath) #
            validation = DataTypeDetector.validate_csv_structure(filepath) #
            results.append((filename, validation))
            
        return results