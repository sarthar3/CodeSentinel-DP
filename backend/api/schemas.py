"""
Pydantic schemas for API request/response models
Defines data contracts between stages
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


# ============================================================================
# Stage 1: RAG Schemas
# ============================================================================

class RAGQueryRequest(BaseModel):
    """Request schema for RAG query"""
    query: str = Field(..., description="User query text")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of results to return")


class RAGSource(BaseModel):
    """Source document information with citation"""
    source: str = Field(..., description="Source filename")
    page: int = Field(..., description="Page number in document")
    excerpt: str = Field(..., description="Relevant text excerpt")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")


class RAGQueryResponse(BaseModel):
    """Response schema for RAG query"""
    answer: str = Field(..., description="Generated answer with citations")
    sources: List[RAGSource] = Field(..., description="Source documents used")
    query: str = Field(..., description="Original query")


# ============================================================================
# Stage 2: Code Porter Schemas
# ============================================================================

class ASTNode(BaseModel):
    """AST node representation"""
    type: str = Field(..., description="Node type (function, class, etc.)")
    name: str = Field(..., description="Node name")
    start_line: int = Field(..., description="Starting line number")
    end_line: int = Field(..., description="Ending line number")
    code: Optional[str] = Field(None, description="Source code")


class MicroserviceSpec(BaseModel):
    """Generated microservice specification"""
    name: str = Field(..., description="Service name")
    description: str = Field(..., description="Service description")
    endpoints: List[Dict[str, Any]] = Field(..., description="API endpoints")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies")
    code: str = Field(..., description="Generated code")
    dockerfile: str = Field(..., description="Generated Dockerfile")
    openapi_spec: Dict[str, Any] = Field(..., description="OpenAPI specification")


class PorterRequest(BaseModel):
    """Request schema for code porter"""
    source_code: str = Field(..., description="Legacy source code")
    language: str = Field(..., description="Source language (php, python, etc.)")
    target_language: str = Field(default="javascript", description="Target language")


class PorterResponse(BaseModel):
    """Response schema for code porter"""
    microservices: List[MicroserviceSpec] = Field(..., description="Generated microservices")
    ast_analysis: List[ASTNode] = Field(..., description="AST analysis results")


# ============================================================================
# Stage 3: QA Agent Schemas
# ============================================================================

class TestFile(BaseModel):
    """Generated test file"""
    filename: str = Field(..., description="Test filename")
    content: str = Field(..., description="Test file content")
    framework: str = Field(..., description="Test framework (jest, pytest, etc.)")


class CoverageReport(BaseModel):
    """Code coverage report"""
    total_coverage: float = Field(..., ge=0.0, le=100.0, description="Total coverage percentage")
    line_coverage: float = Field(..., ge=0.0, le=100.0, description="Line coverage")
    branch_coverage: float = Field(..., ge=0.0, le=100.0, description="Branch coverage")
    files: Dict[str, float] = Field(..., description="Per-file coverage")


class QARequest(BaseModel):
    """Request schema for QA agent"""
    code_path: str = Field(..., description="Path to code directory")
    language: str = Field(..., description="Programming language")


class QAResponse(BaseModel):
    """Response schema for QA agent"""
    test_files: List[TestFile] = Field(..., description="Generated test files")
    coverage: CoverageReport = Field(..., description="Coverage report")
    tests_generated: int = Field(..., description="Number of tests generated")


# ============================================================================
# Stage 4: Triage Agent Schemas
# ============================================================================

class SeverityLevel(str, Enum):
    """Issue severity levels"""
    P1 = "P1"  # Critical
    P2 = "P2"  # High
    P3 = "P3"  # Medium


class TriageResult(BaseModel):
    """Triage analysis result"""
    severity: SeverityLevel = Field(..., description="Assigned severity")
    category: str = Field(..., description="Issue category")
    root_cause: str = Field(..., description="Identified root cause")
    similar_incidents: List[RAGSource] = Field(..., description="Similar past incidents from RAG")
    reproduction_steps: Optional[str] = Field(None, description="Steps to reproduce")
    recommended_action: str = Field(..., description="Recommended action")


class TriageRequest(BaseModel):
    """Request schema for triage agent"""
    issue_title: str = Field(..., description="GitHub issue title")
    issue_body: str = Field(..., description="GitHub issue body")
    issue_number: int = Field(..., description="GitHub issue number")


class TriageResponse(BaseModel):
    """Response schema for triage agent"""
    triage: TriageResult = Field(..., description="Triage analysis")
    comment_posted: bool = Field(..., description="Whether comment was posted to GitHub")


# ============================================================================
# Stage 5: CI/CD Healer Schemas
# ============================================================================

class BuildFailure(BaseModel):
    """Build failure information"""
    job_name: str = Field(..., description="Failed job name")
    error_message: str = Field(..., description="Error message")
    log_excerpt: str = Field(..., description="Relevant log excerpt")
    failed_at: str = Field(..., description="Timestamp of failure")


class PatchInfo(BaseModel):
    """Generated patch information"""
    files_modified: List[str] = Field(..., description="Modified files")
    diff: str = Field(..., description="Unified diff")
    explanation: str = Field(..., description="Explanation of changes")
    pr_url: Optional[str] = Field(None, description="Pull request URL")


class CICDHealRequest(BaseModel):
    """Request schema for CI/CD healer"""
    build_id: str = Field(..., description="Build/workflow ID")
    repository: str = Field(..., description="Repository name")


class CICDHealResponse(BaseModel):
    """Response schema for CI/CD healer"""
    failure: BuildFailure = Field(..., description="Failure analysis")
    patch: PatchInfo = Field(..., description="Generated patch")
    secrets_scanned: bool = Field(..., description="Whether patch was scanned for secrets")


# ============================================================================
# Stage 6: Secret Scanner Schemas
# ============================================================================

class SecretMatch(BaseModel):
    """Detected secret match"""
    line_number: int = Field(..., description="Line number")
    secret_type: str = Field(..., description="Type of secret detected")
    entropy: float = Field(..., description="Shannon entropy")
    matched_pattern: str = Field(..., description="Regex pattern that matched")
    context: str = Field(..., description="Surrounding context")


class ScanRequest(BaseModel):
    """Request schema for secret scanner"""
    file_path: str = Field(..., description="File path to scan")
    content: Optional[str] = Field(None, description="File content (if not reading from disk)")



# ============================================================================
# History Schemas
# ============================================================================

class HistoryResponse(BaseModel):
    id: int
    query: str
    answer: str
    created_at: Any
    
    class Config:
        from_attributes = True

class HistoryCreate(BaseModel):
    query: str
    answer: str

# Made with Bob
