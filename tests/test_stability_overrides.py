from pathlib import Path
from unittest.mock import MagicMock, patch
from deployfilegen.generators.frontend import detect_frontend_framework, generate_frontend_dockerfile, get_frontend_dev_port
from deployfilegen.generators.backend import generate_backend_dockerfile

def test_frontend_overrides():
    # Mock path
    mock_path = MagicMock(spec=Path)
    
    # Test 1: Override Port
    res = detect_frontend_framework(mock_path, override_port=8080)
    assert res["dev_port"] == 8080
    
    # Test 2: Override Command
    res = detect_frontend_framework(mock_path, override_cmd="custom-start")
    assert res["dev_cmd"] == "custom-start"

def test_generate_frontend_dockerfile_with_overrides():
    mock_path = MagicMock(spec=Path)
    (mock_path / "package.json").read_text.return_value = '{"dependencies": {"react": "18"}, "scripts": {"dev": "vite"}}'
    
    dockerfile = generate_frontend_dockerfile("dev", mock_path, override_port=4000, override_cmd="serve")
    assert "EXPOSE 4000" in dockerfile
    assert 'CMD ["npm", "run", "serve"]' in dockerfile

def test_generate_backend_dockerfile_with_override():
    mock_path = MagicMock(spec=Path)
    
    dockerfile = generate_backend_dockerfile("prod", mock_path, override_project_name="my_custom_project")
    assert 'CMD ["gunicorn", "my_custom_project.wsgi:application"' in dockerfile

def test_get_frontend_dev_port_override():
    mock_path = MagicMock(spec=Path)
    port = get_frontend_dev_port(mock_path, override_port=9999)
    assert port == 9999
