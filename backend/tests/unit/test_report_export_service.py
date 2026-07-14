import pytest
from app.application.services.report_export_service import ReportExportService

def test_export_csv():
    data = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Data"}]
    headers = ["id", "name"]
    
    result = ReportExportService.export_data(data, headers, "csv", "Test Export")
    assert isinstance(result, bytes)
    result_str = result.decode("utf-8")
    assert "id,name" in result_str
    assert "1,Test" in result_str

def test_export_excel():
    data = [{"id": 1, "name": "Test"}]
    headers = ["id", "name"]
    
    result = ReportExportService.export_data(data, headers, "xlsx", "Test Export")
    assert isinstance(result, bytes)
    # XLSX files start with PK
    assert result.startswith(b'PK')

def test_export_pdf():
    data = [{"id": 1, "name": "Test"}]
    headers = ["id", "name"]
    
    result = ReportExportService.export_data(data, headers, "pdf", "Test Export")
    assert isinstance(result, bytes)
    assert b"PDF Export for Test Export (Stubbed in Phase 1)" in result
