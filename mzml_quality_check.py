
"""
mzML File Integrity Checker
Validates mzML files converted from .tdf format using pyteomics
"""

import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import traceback
import xml.etree.ElementTree as ET

# Import pyteomics modules
try:
    from pyteomics import mzml
    from pyteomics.xml import unitfloat
except ImportError:
    print("Error: pyteomics not installed. Install with: pip install pyteomics")
    sys.exit(1)

class MzMLIntegrityChecker:
    """Comprehensive mzML file integrity checker"""
    
    def __init__(self, directory_path):
        self.directory_path = Path(directory_path)
        self.results = []
        
    def find_mzml_files(self):
        """Find all mzML files in the directory"""
        mzml_files = list(self.directory_path.glob("*.mzML"))
        mzml_files.extend(list(self.directory_path.glob("*.mzml")))
        return sorted(mzml_files)
    
    def check_xml_validity(self, file_path):
        """Check if the XML structure is valid"""
        try:
            ET.parse(file_path)
            return True, "Valid XML structure"
        except ET.ParseError as e:
            return False, f"XML parse error: {str(e)}"
        except Exception as e:
            return False, f"XML validation error: {str(e)}"
    
    def extract_file_info(self, file_path):
        """Extract basic file information"""
        try:
            stat = file_path.stat()
            return {
                'file_size_mb': round(stat.st_size / (1024*1024), 2),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {
                'file_size_mb': 'Error',
                'modified_time': f'Error: {str(e)}'
            }
    
    def validate_mzml_content(self, file_path):
        """Comprehensive mzML content validation"""
        validation_results = {
            'total_spectra': 0,
            'ms1_spectra': 0,
            'ms2_spectra': 0,
            'min_mz': float('inf'),
            'max_mz': 0,
            'min_rt': float('inf'),
            'max_rt': 0,
            'min_intensity': float('inf'),
            'max_intensity': 0,
            'empty_spectra': 0,
            'invalid_spectra': 0,
            'missing_rt': 0,
            'missing_mz_arrays': 0,
            'missing_intensity_arrays': 0,
            'array_length_mismatches': 0,
            'negative_intensities': 0,
            'zero_intensities': 0,
            'errors': []
        }
        
        try:
            # Open mzML file with pyteomics
            with mzml.MzML(str(file_path)) as reader:
                spectrum_count = 0
                
                for spectrum in reader:
                    spectrum_count += 1
                    validation_results['total_spectra'] = spectrum_count
                    
                    try:
                        # Check MS level
                        ms_level = spectrum.get('ms level', 1)
                        if ms_level == 1:
                            validation_results['ms1_spectra'] += 1
                        elif ms_level == 2:
                            validation_results['ms2_spectra'] += 1
                        
                        # Check retention time
                        rt = spectrum.get('scanList', {}).get('scan', [{}])[0].get('scan start time')
                        if rt is not None:
                            if isinstance(rt, unitfloat):
                                rt_value = float(rt)
                            else:
                                rt_value = float(rt)
                            validation_results['min_rt'] = min(validation_results['min_rt'], rt_value)
                            validation_results['max_rt'] = max(validation_results['max_rt'], rt_value)
                        else:
                            validation_results['missing_rt'] += 1
                        
                        # Check m/z and intensity arrays
                        mz_array = spectrum.get('m/z array')
                        intensity_array = spectrum.get('intensity array')
                        
                        if mz_array is None:
                            validation_results['missing_mz_arrays'] += 1
                        if intensity_array is None:
                            validation_results['missing_intensity_arrays'] += 1
                        
                        if mz_array is not None and intensity_array is not None:
                            # Check array lengths match
                            if len(mz_array) != len(intensity_array):
                                validation_results['array_length_mismatches'] += 1
                            
                            # Check for empty spectra
                            if len(mz_array) == 0 or len(intensity_array) == 0:
                                validation_results['empty_spectra'] += 1
                            else:
                                # Update m/z range
                                validation_results['min_mz'] = min(validation_results['min_mz'], min(mz_array))
                                validation_results['max_mz'] = max(validation_results['max_mz'], max(mz_array))
                                
                                # Update intensity range
                                validation_results['min_intensity'] = min(validation_results['min_intensity'], min(intensity_array))
                                validation_results['max_intensity'] = max(validation_results['max_intensity'], max(intensity_array))
                                
                                # Check for negative intensities
                                negative_count = sum(1 for i in intensity_array if i < 0)
                                validation_results['negative_intensities'] += negative_count
                                
                                # Check for zero intensities
                                zero_count = sum(1 for i in intensity_array if i == 0)
                                validation_results['zero_intensities'] += zero_count
                        
                    except Exception as e:
                        validation_results['invalid_spectra'] += 1
                        validation_results['errors'].append(f"Spectrum {spectrum_count}: {str(e)}")
                    
                    # Limit error collection to prevent memory issues
                    if len(validation_results['errors']) > 10:
                        validation_results['errors'].append("... (additional errors truncated)")
                        break
                        
        except Exception as e:
            validation_results['errors'].append(f"Reader error: {str(e)}")
            return validation_results
        
        # Clean up infinite values
        if validation_results['min_mz'] == float('inf'):
            validation_results['min_mz'] = 0
        if validation_results['min_rt'] == float('inf'):
            validation_results['min_rt'] = 0
        if validation_results['min_intensity'] == float('inf'):
            validation_results['min_intensity'] = 0
        
        return validation_results
    
    def assess_file_integrity(self, file_path):
        """Assess overall file integrity"""
        print(f"\n--- Checking: {file_path.name} ---")
        
        # Initialize result dictionary
        result = {
            'filename': file_path.name,
            'file_path': str(file_path),
            'status': 'UNKNOWN',
            'issues': [],
            'warnings': []
        }
        
        # Extract file info
        file_info = self.extract_file_info(file_path)
        result.update(file_info)
        
        # Check if file exists and is readable
        if not file_path.exists():
            result['status'] = 'FAILED'
            result['issues'].append('File does not exist')
            return result
        
        if file_info['file_size_mb'] == 0:
            result['status'] = 'FAILED'
            result['issues'].append('File is empty')
            return result
        
        # Check XML validity
        xml_valid, xml_message = self.check_xml_validity(file_path)
        if not xml_valid:
            result['status'] = 'FAILED'
            result['issues'].append(f'Invalid XML: {xml_message}')
            return result
        
        # Validate mzML content
        try:
            validation = self.validate_mzml_content(file_path)
            result.update(validation)
            
            # Assess integrity based on validation results
            if validation['total_spectra'] == 0:
                result['status'] = 'FAILED'
                result['issues'].append('No spectra found')
            elif validation['invalid_spectra'] > validation['total_spectra'] * 0.1:  # More than 10% invalid
                result['status'] = 'FAILED'
                result['issues'].append(f'High number of invalid spectra: {validation["invalid_spectra"]}')
            elif validation['missing_mz_arrays'] > 0 or validation['missing_intensity_arrays'] > 0:
                result['status'] = 'FAILED'
                result['issues'].append('Missing essential data arrays')
            elif validation['array_length_mismatches'] > 0:
                result['status'] = 'FAILED'
                result['issues'].append('m/z and intensity array length mismatches')
            else:
                result['status'] = 'PASSED'
                
                # Add warnings for potential issues
                if validation['empty_spectra'] > 0:
                    result['warnings'].append(f'{validation["empty_spectra"]} empty spectra')
                if validation['missing_rt'] > 0:
                    result['warnings'].append(f'{validation["missing_rt"]} spectra missing retention time')
                if validation['negative_intensities'] > 0:
                    result['warnings'].append(f'{validation["negative_intensities"]} negative intensity values')
            
        except Exception as e:
            result['status'] = 'FAILED'
            result['issues'].append(f'Validation error: {str(e)}')
            result['errors'] = [traceback.format_exc()]
        
        # Print summary
        status_symbol = "✓" if result['status'] == 'PASSED' else "✗"
        print(f"{status_symbol} {result['status']}: {result['filename']}")
        if result['status'] == 'PASSED':
            print(f"  Spectra: {result.get('total_spectra', 0)} (MS1: {result.get('ms1_spectra', 0)}, MS2: {result.get('ms2_spectra', 0)})")
            print(f"  m/z range: {result.get('min_mz', 0):.1f} - {result.get('max_mz', 0):.1f}")
            print(f"  RT range: {result.get('min_rt', 0):.2f} - {result.get('max_rt', 0):.2f} min")
        
        if result['issues']:
            print(f"  Issues: {'; '.join(result['issues'])}")
        if result['warnings']:
            print(f"  Warnings: {'; '.join(result['warnings'])}")
        
        return result
    
    def run_integrity_check(self):
        """Run integrity check on all mzML files in directory"""
        print(f"mzML File Integrity Checker")
        print(f"Directory: {self.directory_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Find mzML files
        mzml_files = self.find_mzml_files()
        
        if not mzml_files:
            print(f"\nNo mzML files found in {self.directory_path}")
            return
        
        print(f"\nFound {len(mzml_files)} mzML files")
        
        # Check each file
        for file_path in mzml_files:
            result = self.assess_file_integrity(file_path)
            self.results.append(result)
        
        # Generate summary
        self.generate_summary()
        
        # Save detailed report
        self.save_detailed_report()
    
    def generate_summary(self):
        """Generate and display summary statistics"""
        if not self.results:
            return
        
        passed = sum(1 for r in self.results if r['status'] == 'PASSED')
        failed = sum(1 for r in self.results if r['status'] == 'FAILED')
        total = len(self.results)
        
        print(f"\n{'='*50}")
        print(f"INTEGRITY CHECK SUMMARY")
        print(f"{'='*50}")
        print(f"Total files checked: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        
        if failed > 0:
            print(f"\nFAILED FILES:")
            for result in self.results:
                if result['status'] == 'FAILED':
                    print(f"  ✗ {result['filename']}: {'; '.join(result['issues'])}")
        
        # Statistics for passed files
        passed_results = [r for r in self.results if r['status'] == 'PASSED']
        if passed_results:
            total_spectra = sum(r.get('total_spectra', 0) for r in passed_results)
            total_ms1 = sum(r.get('ms1_spectra', 0) for r in passed_results)
            total_ms2 = sum(r.get('ms2_spectra', 0) for r in passed_results)
            
            print(f"\nSTATISTICS (Passed files):")
            print(f"  Total spectra: {total_spectra:,}")
            print(f"  MS1 spectra: {total_ms1:,}")
            print(f"  MS2 spectra: {total_ms2:,}")
            print(f"  Average file size: {sum(r.get('file_size_mb', 0) for r in passed_results)/len(passed_results):.1f} MB")
    
    def save_detailed_report(self):
        """Save detailed report to CSV file"""
        if not self.results:
            return
        
        # Prepare data for CSV
        csv_data = []
        for result in self.results:
            row = {
                'filename': result['filename'],
                'status': result['status'],
                'file_size_mb': result.get('file_size_mb', ''),
                'total_spectra': result.get('total_spectra', ''),
                'ms1_spectra': result.get('ms1_spectra', ''),
                'ms2_spectra': result.get('ms2_spectra', ''),
                'min_mz': result.get('min_mz', ''),
                'max_mz': result.get('max_mz', ''),
                'min_rt': result.get('min_rt', ''),
                'max_rt': result.get('max_rt', ''),
                'empty_spectra': result.get('empty_spectra', ''),
                'invalid_spectra': result.get('invalid_spectra', ''),
                'missing_rt': result.get('missing_rt', ''),
                'array_mismatches': result.get('array_length_mismatches', ''),
                'negative_intensities': result.get('negative_intensities', ''),
                'issues': '; '.join(result.get('issues', [])),
                'warnings': '; '.join(result.get('warnings', [])),
                'modified_time': result.get('modified_time', '')
            }
            csv_data.append(row)
        
        # Save to CSV
        df = pd.DataFrame(csv_data)
        output_file = self.directory_path / f"mzML_integrity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False)
        print(f"\nDetailed report saved to: {output_file}")


def main():
    """Main function to run the integrity checker"""
    
    # Directory containing mzML files
    directory = r"/content/drive/MyDrive/Utrecht_Oncode_pipeline"
    
    # Create and run integrity checker
    checker = MzMLIntegrityChecker(directory)
    checker.run_integrity_check()


if __name__ == "__main__":
    main()
