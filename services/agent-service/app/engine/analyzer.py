import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from app.storage.models import Finding, FindingSeverity, FindingCategory

@dataclass
class AnalysisResult:
    files_analyzed: int
    api_routes: List[str]
    components: List[str]
    issues: List[Dict[str, Any]]

class CodeAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.issues: List[Dict[str, Any]] = []
    
    def analyze(self) -> AnalysisResult:
        self.issues = []
        api_routes = []
        components = []
        files_analyzed = 0
        
        if not self.project_path.exists():
            return AnalysisResult(
                files_analyzed=0,
                api_routes=[],
                components=[],
                issues=[{
                    "category": FindingCategory.FUNCTIONALITY.value,
                    "severity": FindingSeverity.HIGH.value,
                    "title": "项目路径不存在",
                    "description": f"指定的代码路径 {self.project_path} 不存在"
                }]
            )
        
        backend_path = self.project_path / "app"
        if backend_path.exists():
            files_analyzed += self._analyze_python_code(backend_path)
            api_routes = self._find_api_routes(backend_path)
        
        frontend_path = Path("/workspace/apps/desktop-client/src")
        if frontend_path.exists():
            components = self._analyze_vue_components(frontend_path)
        
        return AnalysisResult(
            files_analyzed=files_analyzed,
            api_routes=api_routes,
            components=components,
            issues=self.issues
        )
    
    def _analyze_python_code(self, path: Path) -> int:
        count = 0
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    count += 1
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self._check_security_issues(file_path, content)
                        self._check_error_handling(file_path, content)
                        self._check_performance_issues(file_path, content)
                    except Exception:
                        pass
        return count
    
    def _check_security_issues(self, file_path: Path, content: str):
        if any(secret in content.lower() for secret in ['password=', 'api_key=', 'secret=']):
            if 'os.environ' not in content and '.env' not in content:
                self.issues.append({
                    "category": FindingCategory.SECURITY.value,
                    "severity": FindingSeverity.HIGH.value,
                    "title": "可能的硬编码密钥",
                    "description": f"文件 {file_path.name} 中可能存在硬编码的密钥或密码",
                    "location": str(file_path)
                })
    
    def _check_error_handling(self, file_path: Path, content: str):
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    has_error_handling = any(
                        isinstance(n, ast.ExceptHandler) for n in ast.walk(node)
                    )
                    if not has_error_handling and len(list(ast.walk(node))) > 10:
                        self.issues.append({
                            "category": FindingCategory.USABILITY.value,
                            "severity": FindingSeverity.LOW.value,
                            "title": "缺少错误处理",
                            "description": f"函数 {node.name} 可能缺少错误处理",
                            "location": f"{file_path}:{node.lineno}"
                        })
        except SyntaxError:
            pass
    
    def _check_performance_issues(self, file_path: Path, content: str):
        if 'requests.' in content and 'async' not in content:
            self.issues.append({
                "category": FindingCategory.PERFORMANCE.value,
                "severity": FindingSeverity.LOW.value,
                "title": "可能的同步阻塞",
                "description": f"文件 {file_path.name} 中使用同步 requests 库，可能影响性能",
                "location": str(file_path)
            })
    
    def _find_api_routes(self, path: Path) -> List[str]:
        routes = []
        api_dir = path / "api"
        if api_dir.exists():
            for file in api_dir.rglob("*.py"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    route_patterns = re.findall(r'@(?:router|app)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)', content)
                    for method, route in route_patterns:
                        routes.append(f"{method.upper()} {route}")
                except Exception:
                    pass
        return routes
    
    def _analyze_vue_components(self, path: Path) -> List[str]:
        components = []
        for file in path.rglob("*.vue"):
            components.append(str(file.relative_to(path)))
        return components
