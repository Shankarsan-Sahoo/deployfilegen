import pytest
from pathlib import Path
from deployfilegen.analyzer.detector import detect_django_backend, detect_react_frontend
from deployfilegen.exceptions import DetectionError, ProjectStructureError

def test_detect_django_backend(tmp_path):
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    manage_py = backend_dir / "manage.py"
    manage_py.write_text("print('django')")
    
    path = detect_django_backend(tmp_path)
    assert path == backend_dir

def test_detect_django_backend_missing(tmp_path):
    with pytest.raises(ProjectStructureError):
        detect_django_backend(tmp_path)

def test_detect_react_frontend(tmp_path):
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    package_json = frontend_dir / "package.json"
    package_json.write_text("{}")
    
    path = detect_react_frontend(tmp_path)
    assert path == frontend_dir

def test_detect_react_frontend_missing(tmp_path):
    with pytest.raises(ProjectStructureError):
        detect_react_frontend(tmp_path)
