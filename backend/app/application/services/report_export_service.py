import csv
import io
from typing import List, Dict, Any
import openpyxl


class ReportExportService:
    @staticmethod
    def _export_csv(data: List[Dict[str, Any]], headers: List[str]) -> bytes:
        if not data:
            return b""
            
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow({h: row.get(h, "") for h in headers})
        
        return output.getvalue().encode('utf-8')

    @staticmethod
    def _export_excel(data: List[Dict[str, Any]], headers: List[str]) -> bytes:
        if not data:
            return b""
            
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(headers)
        
        for row in data:
            ws.append([row.get(h, "") for h in headers])
            
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    @staticmethod
    def _export_pdf(data: List[Dict[str, Any]], headers: List[str], title: str) -> bytes:
        # Stub for PDF using reportlab if we wanted to build complex layouts.
        # For phase 1, we return a simple string or placeholder.
        # A real implementation would use reportlab.platypus.Table.
        return f"PDF Export for {title} (Stubbed in Phase 1)".encode('utf-8')

    @staticmethod
    def export_data(data: List[Dict[str, Any]], headers: List[str], format: str, title: str) -> bytes:
        if format == 'csv':
            return ReportExportService._export_csv(data, headers)
        elif format == 'xlsx':
            return ReportExportService._export_excel(data, headers)
        elif format == 'pdf':
            return ReportExportService._export_pdf(data, headers, title)
        else:
            raise ValueError(f"Unsupported format: {format}")

    # Specific exports based on module
    @staticmethod
    def export_dashboard(data: Dict[str, Any], format: str) -> bytes:
        headers = list(data.keys())
        return ReportExportService.export_data([data], headers, format, "Dashboard KPI")

    @staticmethod
    def export_trips(data: List[Dict[str, Any]], format: str) -> bytes:
        headers = ["status", "count"] if data else []
        return ReportExportService.export_data(data, headers, format, "Trip Statistics")
        
    @staticmethod
    def export_fuel(data: List[Dict[str, Any]], format: str) -> bytes:
        headers = ["tractor", "total_liters", "average_kmpl", "cost_per_km", "fuel_cost", "suspicious_transactions"] if data else []
        return ReportExportService.export_data(data, headers, format, "Fuel Analytics")

    @staticmethod
    def export_profitability(data: List[Dict[str, Any]], format: str) -> bytes:
        headers = ["tractor", "trip_count", "income", "fuel_cost", "maintenance_cost", "trip_expense", "profit"] if data else []
        return ReportExportService.export_data(data, headers, format, "Tractor Profitability")
