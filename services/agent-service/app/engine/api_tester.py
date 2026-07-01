import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio

@dataclass
class ApiTestResult:
    endpoint: str
    method: str
    success: bool
    status_code: Optional[int]
    response_time: float
    error: Optional[str] = None
    response_data: Optional[Any] = None

class ApiTester:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.results: List[ApiTestResult] = []
    
    async def test_endpoint(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> ApiTestResult:
        url = f"{self.base_url}/{path.lstrip('/')}"
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                elapsed = asyncio.get_event_loop().time() - start_time
                result = ApiTestResult(
                    endpoint=path,
                    method=method,
                    success=response.status_code < 400,
                    status_code=response.status_code,
                    response_time=elapsed,
                    response_data=response.json() if response.status_code < 400 else None,
                    error=None if response.status_code < 400 else response.text
                )
        except Exception as e:
            elapsed = asyncio.get_event_loop().time() - start_time
            result = ApiTestResult(
                endpoint=path,
                method=method,
                success=False,
                status_code=None,
                response_time=elapsed,
                error=str(e)
            )
        
        self.results.append(result)
        return result
    
    async def test_project_crud(self) -> Dict[str, Any]:
        project_id = None
        operations = {"create": None, "list": None, "get": None, "delete": None}
        
        result = await self.test_endpoint("POST", "/api/v1/projects", {
            "name": "Test Project",
            "type": "novel",
            "description": "Agent evaluation test project"
        })
        operations["create"] = result
        if result.success and result.response_data:
            project_id = result.response_data.get("id")
        
        if project_id:
            result = await self.test_endpoint("GET", "/api/v1/projects")
            operations["list"] = result
        
        if project_id:
            result = await self.test_endpoint("GET", f"/api/v1/projects/{project_id}")
            operations["get"] = result
        
        if project_id:
            result = await self.test_endpoint("DELETE", f"/api/v1/projects/{project_id}")
            operations["delete"] = result
        
        return operations
    
    async def test_chapter_crud(self, project_id: str) -> Dict[str, Any]:
        chapter_id = None
        operations = {"create": None, "list": None, "get": None, "update": None}
        
        result = await self.test_endpoint("POST", f"/api/v1/projects/{project_id}/chapters", {
            "title": "Test Chapter",
            "content": "This is a test chapter for agent evaluation.",
            "order_index": 1
        })
        operations["create"] = result
        if result.success and result.response_data:
            chapter_id = result.response_data.get("id")
        
        result = await self.test_endpoint("GET", f"/api/v1/projects/{project_id}/chapters")
        operations["list"] = result
        
        if chapter_id:
            result = await self.test_endpoint("GET", f"/api/v1/chapters/{chapter_id}")
            operations["get"] = result
        
        if chapter_id:
            result = await self.test_endpoint("PUT", f"/api/v1/chapters/{chapter_id}", {
                "content": "Updated test chapter content."
            })
            operations["update"] = result
        
        return operations
    
    async def test_generation(self, project_id: str, chapter_id: str) -> Dict[str, Any]:
        results = {}
        
        result = await self.test_endpoint("POST", "/api/v1/generate/ideas", {
            "project_id": project_id,
            "prompt": "测试创意生成",
            "model": "mock"
        })
        results["ideas"] = result
        
        result = await self.test_endpoint("POST", "/api/v1/generate/chapter", {
            "project_id": project_id,
            "chapter_id": chapter_id,
            "prompt": "续写章节内容",
            "model": "mock"
        })
        results["chapter"] = result
        
        return results
    
    async def test_export(self, project_id: str) -> Dict[str, Any]:
        results = {}
        
        result = await self.test_endpoint("POST", f"/api/v1/export/{project_id}/epub")
        results["epub"] = result
        
        result = await self.test_endpoint("POST", f"/api/v1/export/{project_id}/pdf")
        results["pdf"] = result
        
        return results
    
    async def test_memory(self, project_id: str, chapter_id: str) -> Dict[str, Any]:
        results = {}
        
        result = await self.test_endpoint(
            "POST",
            f"/api/v1/memory/projects/{project_id}/extract",
            {"chapter_id": chapter_id}
        )
        results["extract"] = result
        
        result = await self.test_endpoint(
            "POST",
            f"/api/v1/memory/projects/{project_id}/search",
            {"query": "测试"}
        )
        results["search"] = result
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        avg_response_time = sum(r.response_time for r in self.results) / total if total > 0 else 0
        
        return {
            "total_requests": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "average_response_time": round(avg_response_time, 3),
            "p95_response_time": self._calculate_percentile(95),
            "results": self.results
        }
    
    def _calculate_percentile(self, percentile: int) -> float:
        if not self.results:
            return 0
        sorted_times = sorted(r.response_time for r in self.results)
        index = int(len(sorted_times) * percentile / 100)
        return round(sorted_times[min(index, len(sorted_times) - 1)], 3)
