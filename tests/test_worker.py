# tests/test_worker.py
# Unit tests for Worker module

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QThread
from main_window.worker import Worker


class TestWorker:
    """Test cases for Worker class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.worker = Worker()

    def test_init(self):
        """Test Worker initialization."""
        assert self.worker is not None
        assert isinstance(self.worker, QThread)
        assert hasattr(self.worker, 'run')
        assert hasattr(self.worker, 'stop')

    def test_set_nsis_codes(self):
        """Test setting NSIS codes."""
        codes = ["TEST001", "TEST002", "TEST003"]
        self.worker.set_nsis_codes(codes)
        assert self.worker.nsis_codes == codes

    def test_set_nsis_codes_empty(self):
        """Test setting empty NSIS codes."""
        self.worker.set_nsis_codes([])
        assert self.worker.nsis_codes == []

    def test_set_nsis_codes_none(self):
        """Test setting None NSIS codes."""
        self.worker.set_nsis_codes(None)
        assert self.worker.nsis_codes == []

    def test_set_web_automation(self):
        """Test setting web automation instance."""
        mock_automation = Mock()
        self.worker.set_web_automation(mock_automation)
        assert self.worker.web_automation == mock_automation

    def test_set_excel_handler(self):
        """Test setting Excel handler instance."""
        mock_excel_handler = Mock()
        self.worker.set_excel_handler(mock_excel_handler)
        assert self.worker.excel_handler == mock_excel_handler

    def test_set_output_file(self):
        """Test setting output file path."""
        output_file = "test_output.xlsx"
        self.worker.set_output_file(output_file)
        assert self.worker.output_file == output_file

    def test_stop_processing(self):
        """Test stopping processing."""
        self.worker.stop_processing()
        assert self.worker.should_stop is True

    def test_reset_stop_flag(self):
        """Test resetting stop flag."""
        self.worker.should_stop = True
        self.worker.reset_stop_flag()
        assert self.worker.should_stop is False

    @patch('main_window.worker.time.sleep')
    def test_run_with_no_codes(self, mock_sleep):
        """Test run method with no NSIS codes."""
        self.worker.nsis_codes = []
        self.worker.run()
        
        # Should not process anything
        mock_sleep.assert_not_called()

    @patch('main_window.worker.time.sleep')
    def test_run_with_codes_but_no_automation(self, mock_sleep):
        """Test run method with codes but no web automation."""
        self.worker.nsis_codes = ["TEST001", "TEST002"]
        self.worker.web_automation = None
        self.worker.run()
        
        # Should not process anything
        mock_sleep.assert_not_called()

    @patch('main_window.worker.time.sleep')
    def test_run_with_codes_but_no_excel_handler(self, mock_sleep):
        """Test run method with codes but no Excel handler."""
        self.worker.nsis_codes = ["TEST001", "TEST002"]
        self.worker.web_automation = Mock()
        self.worker.excel_handler = None
        self.worker.run()
        
        # Should not process anything
        mock_sleep.assert_not_called()

    @patch('main_window.worker.time.sleep')
    def test_run_processing_success(self, mock_sleep):
        """Test successful processing run."""
        # Setup mocks
        mock_automation = Mock()
        mock_excel_handler = Mock()
        
        self.worker.nsis_codes = ["TEST001", "TEST002"]
        self.worker.web_automation = mock_automation
        self.worker.excel_handler = mock_excel_handler
        self.worker.should_stop = False
        
        # Mock successful fetch
        mock_automation.fetch_nsis_status.return_value = {
            "status": "Completed",
            "result": "Success"
        }
        
        # Run processing
        self.worker.run()
        
        # Verify calls
        assert mock_automation.fetch_nsis_status.call_count == 2
        mock_sleep.assert_called()

    @patch('main_window.worker.time.sleep')
    def test_run_processing_with_stop(self, mock_sleep):
        """Test processing run with stop signal."""
        # Setup mocks
        mock_automation = Mock()
        mock_excel_handler = Mock()
        
        self.worker.nsis_codes = ["TEST001", "TEST002", "TEST003"]
        self.worker.web_automation = mock_automation
        self.worker.excel_handler = mock_excel_handler
        self.worker.should_stop = False
        
        # Mock successful fetch for first code, then stop
        def fetch_side_effect(code):
            if code == "TEST001":
                self.worker.should_stop = True
                return {"status": "Completed", "result": "Success"}
            return {"status": "Pending", "result": "Waiting"}
        
        mock_automation.fetch_nsis_status.side_effect = fetch_side_effect
        
        # Run processing
        self.worker.run()
        
        # Should only process first code
        assert mock_automation.fetch_nsis_status.call_count == 1

    @patch('main_window.worker.time.sleep')
    def test_run_processing_with_error(self, mock_sleep):
        """Test processing run with error."""
        # Setup mocks
        mock_automation = Mock()
        mock_excel_handler = Mock()
        
        self.worker.nsis_codes = ["TEST001"]
        self.worker.web_automation = mock_automation
        self.worker.excel_handler = mock_excel_handler
        self.worker.should_stop = False
        
        # Mock error in fetch
        mock_automation.fetch_nsis_status.side_effect = Exception("Network error")
        
        # Run processing
        self.worker.run()
        
        # Should still complete
        mock_automation.fetch_nsis_status.assert_called_once()

    def test_simulate_fetch_result_success(self):
        """Test successful fetch result simulation."""
        result = self.worker._simulate_fetch_result("TEST001")
        
        assert result is not None
        assert "status" in result
        assert "result" in result
        assert "timestamp" in result

    def test_simulate_fetch_result_error(self):
        """Test fetch result simulation with error."""
        # Mock random to always return error
        with patch('main_window.worker.random.random', return_value=0.9):
            result = self.worker._simulate_fetch_result("TEST001")
            
            assert result is not None
            assert result["status"] == "Error"
            assert "error" in result["result"]

    def test_process_nsis_code_success(self):
        """Test successful NSIS code processing."""
        mock_automation = Mock()
        mock_automation.fetch_nsis_status.return_value = {
            "status": "Completed",
            "result": "Success"
        }
        
        self.worker.web_automation = mock_automation
        
        result = self.worker._process_nsis_code("TEST001")
        
        assert result is not None
        assert result["nsis_code"] == "TEST001"
        assert result["status"] == "Completed"
        mock_automation.fetch_nsis_status.assert_called_once_with("TEST001")

    def test_process_nsis_code_error(self):
        """Test NSIS code processing with error."""
        mock_automation = Mock()
        mock_automation.fetch_nsis_status.side_effect = Exception("Network error")
        
        self.worker.web_automation = mock_automation
        
        result = self.worker._process_nsis_code("TEST001")
        
        assert result is not None
        assert result["nsis_code"] == "TEST001"
        assert result["status"] == "Error"
        assert "Network error" in result["result"]

    def test_process_nsis_code_no_automation(self):
        """Test NSIS code processing without automation."""
        self.worker.web_automation = None
        
        result = self.worker._process_nsis_code("TEST001")
        
        assert result is not None
        assert result["nsis_code"] == "TEST001"
        assert result["status"] == "Error"
        assert "No web automation" in result["result"]

    def test_save_results_success(self):
        """Test successful results saving."""
        mock_excel_handler = Mock()
        mock_excel_handler.write_excel.return_value = True
        
        self.worker.excel_handler = mock_excel_handler
        self.worker.output_file = "test_output.xlsx"
        
        results = [
            {"nsis_code": "TEST001", "status": "Completed"},
            {"nsis_code": "TEST002", "status": "Error"}
        ]
        
        success = self.worker._save_results(results)
        
        assert success is True
        mock_excel_handler.write_excel.assert_called_once()

    def test_save_results_no_excel_handler(self):
        """Test results saving without Excel handler."""
        self.worker.excel_handler = None
        
        results = [{"nsis_code": "TEST001", "status": "Completed"}]
        
        success = self.worker._save_results(results)
        
        assert success is False

    def test_save_results_no_output_file(self):
        """Test results saving without output file."""
        mock_excel_handler = Mock()
        self.worker.excel_handler = mock_excel_handler
        self.worker.output_file = None
        
        results = [{"nsis_code": "TEST001", "status": "Completed"}]
        
        success = self.worker._save_results(results)
        
        assert success is False

    def test_save_results_excel_error(self):
        """Test results saving with Excel error."""
        mock_excel_handler = Mock()
        mock_excel_handler.write_excel.return_value = False
        
        self.worker.excel_handler = mock_excel_handler
        self.worker.output_file = "test_output.xlsx"
        
        results = [{"nsis_code": "TEST001", "status": "Completed"}]
        
        success = self.worker._save_results(results)
        
        assert success is False

    def test_get_processing_stats(self):
        """Test getting processing statistics."""
        results = [
            {"nsis_code": "TEST001", "status": "Completed"},
            {"nsis_code": "TEST002", "status": "Error"},
            {"nsis_code": "TEST003", "status": "Completed"},
            {"nsis_code": "TEST004", "status": "Pending"}
        ]
        
        stats = self.worker._get_processing_stats(results)
        
        assert stats["total"] == 4
        assert stats["completed"] == 2
        assert stats["error"] == 1
        assert stats["pending"] == 1 