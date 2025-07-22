# tests/test_excel_handler.py
# Unit tests for ExcelHandler module

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from main_window.excel_handler import ExcelHandler
from config import COL_RICERCA, COL_STATO, COL_PROTOCOLLO, COL_PROVVEDIMENTO, COL_DATA_PROVV, COL_CODICE_RIS, COL_NOTE


class TestExcelHandler:
    """Test cases for ExcelHandler class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.excel_handler = ExcelHandler()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test fixtures."""
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_init(self):
        """Test ExcelHandler initialization."""
        assert self.excel_handler is not None
        assert hasattr(self.excel_handler, 'read_excel')
        assert hasattr(self.excel_handler, 'write_excel')

    def test_validate_file_path_valid(self):
        """Test file path validation with valid path."""
        # Create a temporary Excel file
        temp_file = os.path.join(self.temp_dir, "test.xlsx")
        with open(temp_file, 'w') as f:
            f.write("test")
        
        result = self.excel_handler._validate_file_path(temp_file)
        assert result is True

    def test_validate_file_path_invalid_extension(self):
        """Test file path validation with invalid extension."""
        temp_file = os.path.join(self.temp_dir, "test.txt")
        with open(temp_file, 'w') as f:
            f.write("test")
        
        result = self.excel_handler._validate_file_path(temp_file)
        assert result is False

    def test_validate_file_path_nonexistent(self):
        """Test file path validation with nonexistent file."""
        temp_file = os.path.join(self.temp_dir, "nonexistent.xlsx")
        
        result = self.excel_handler._validate_file_path(temp_file)
        assert result is False

    def test_validate_file_path_none(self):
        """Test file path validation with None."""
        result = self.excel_handler._validate_file_path(None)
        assert result is False

    def test_validate_file_path_empty(self):
        """Test file path validation with empty string."""
        result = self.excel_handler._validate_file_path("")
        assert result is False

    @patch('main_window.excel_handler.openpyxl.load_workbook')
    def test_read_excel_success(self, mock_load_workbook):
        """Test successful Excel reading."""
        # Mock workbook and worksheet
        mock_workbook = Mock()
        mock_worksheet = Mock()
        mock_workbook.active = mock_worksheet
        
        # Mock cell values
        mock_worksheet.iter_rows.return_value = [
            [Mock(value="NSIS Code"), Mock(value="Status")],
            [Mock(value="TEST001"), Mock(value="Pending")],
            [Mock(value="TEST002"), Mock(value="Completed")]
        ]
        
        mock_load_workbook.return_value = mock_workbook
        
        # Test reading
        result = self.excel_handler.read_excel("test.xlsx")
        
        assert result is not None
        assert len(result) == 2  # 2 data rows
        assert result[0]["NSIS Code"] == "TEST001"
        assert result[0]["Status"] == "Pending"

    @patch('main_window.excel_handler.openpyxl.load_workbook')
    def test_read_excel_file_not_found(self, mock_load_workbook):
        """Test Excel reading with file not found."""
        mock_load_workbook.side_effect = FileNotFoundError("File not found")
        
        result = self.excel_handler.read_excel("nonexistent.xlsx")
        assert result is None

    @patch('main_window.excel_handler.openpyxl.load_workbook')
    def test_read_excel_permission_error(self, mock_load_workbook):
        """Test Excel reading with permission error."""
        mock_load_workbook.side_effect = PermissionError("Permission denied")
        
        result = self.excel_handler.read_excel("protected.xlsx")
        assert result is None

    @patch('main_window.excel_handler.openpyxl.load_workbook')
    def test_read_excel_invalid_format(self, mock_load_workbook):
        """Test Excel reading with invalid format."""
        mock_load_workbook.side_effect = ValueError("Invalid format")
        
        result = self.excel_handler.read_excel("invalid.xlsx")
        assert result is None

    def test_extract_nsis_codes_empty_data(self):
        """Test NSIS code extraction with empty data."""
        result = self.excel_handler._extract_nsis_codes([])
        assert result == []

    def test_extract_nsis_codes_valid_data(self):
        """Test NSIS code extraction with valid data."""
        data = [
            {"NSIS Code": "TEST001", "Status": "Pending"},
            {"NSIS Code": "TEST002", "Status": "Completed"},
            {"NSIS Code": "", "Status": "Pending"},  # Empty code
            {"Status": "Pending"}  # Missing NSIS Code key
        ]
        
        result = self.excel_handler._extract_nsis_codes(data)
        assert result == ["TEST001", "TEST002"]

    def test_extract_nsis_codes_none_data(self):
        """Test NSIS code extraction with None data."""
        result = self.excel_handler._extract_nsis_codes(None)
        assert result == []

    def test_validate_nsis_code_valid(self):
        """Test NSIS code validation with valid codes."""
        valid_codes = ["TEST001", "NSIS123", "ABC123456"]
        
        for code in valid_codes:
            result = self.excel_handler._validate_nsis_code(code)
            assert result is True

    def test_validate_nsis_code_invalid(self):
        """Test NSIS code validation with invalid codes."""
        invalid_codes = ["", None, "123", "TEST", "A" * 50]  # Too long
        
        for code in invalid_codes:
            result = self.excel_handler._validate_nsis_code(code)
            assert result is False

    @patch('main_window.excel_handler.openpyxl.Workbook')
    def test_write_excel_success(self, mock_workbook):
        """Test successful Excel writing."""
        # Mock workbook and worksheet
        mock_wb = Mock()
        mock_ws = Mock()
        mock_workbook.return_value = mock_wb
        mock_wb.active = mock_ws
        
        data = [
            {"NSIS Code": "TEST001", "Status": "Completed", "Result": "Success"},
            {"NSIS Code": "TEST002", "Status": "Error", "Result": "Failed"}
        ]
        
        temp_file = os.path.join(self.temp_dir, "output.xlsx")
        result = self.excel_handler.write_excel(data, temp_file)
        
        assert result is True
        mock_wb.save.assert_called_once_with(temp_file)

    def test_write_excel_no_data(self):
        """Test Excel writing with no data."""
        temp_file = os.path.join(self.temp_dir, "output.xlsx")
        result = self.excel_handler.write_excel([], temp_file)
        assert result is False

    def test_write_excel_none_data(self):
        """Test Excel writing with None data."""
        temp_file = os.path.join(self.temp_dir, "output.xlsx")
        result = self.excel_handler.write_excel(None, temp_file)
        assert result is False

    def test_write_excel_invalid_path(self):
        """Test Excel writing with invalid path."""
        result = self.excel_handler.write_excel([{"test": "data"}], "")
        assert result is False

    @patch('main_window.excel_handler.openpyxl.Workbook')
    def test_write_excel_permission_error(self, mock_workbook):
        """Test Excel writing with permission error."""
        mock_wb = Mock()
        mock_workbook.return_value = mock_wb
        mock_wb.save.side_effect = PermissionError("Permission denied")
        
        temp_file = os.path.join(self.temp_dir, "output.xlsx")
        result = self.excel_handler.write_excel([{"test": "data"}], temp_file)
        assert result is False

    def test_get_column_index_valid(self):
        """Test getting valid column index."""
        headers = ["NSIS Code", "Status", "Result"]
        
        index = self.excel_handler._get_column_index(headers, "Status")
        assert index == 1

    def test_get_column_index_not_found(self):
        """Test getting column index for non-existent column."""
        headers = ["NSIS Code", "Status"]
        
        index = self.excel_handler._get_column_index(headers, "NonExistent")
        assert index == -1

    def test_get_column_index_empty_headers(self):
        """Test getting column index with empty headers."""
        index = self.excel_handler._get_column_index([], "Status")
        assert index == -1 