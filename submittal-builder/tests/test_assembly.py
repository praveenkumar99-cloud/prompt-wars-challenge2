import pytest
import os
from app.services.assembly_service import AssemblyService

def test_assembly_missing_report_generation(tmp_path):
    service = AssemblyService()
    job_id = "test-job-123"
    missing_parts = ["MISSING-1", "MISSING-2"]
    
    output_dir = str(tmp_path)
    report_path = service._generate_missing_report(job_id, missing_parts, output_dir)
    
    assert os.path.exists(report_path)
    with open(report_path, "r") as f:
        content = f.read()
        assert "MISSING PARTS REPORT" in content
        assert "test-job-123" in content
        assert "MISSING-1" in content
        assert "MISSING-2" in content
