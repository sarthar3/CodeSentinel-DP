"""
Documentation & Test Pipeline API Router
Handles automated documentation and test generation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ..doc_test_pipeline.doc_generator import DocumentationGenerator
from ..doc_test_pipeline.test_generator import TestGenerator

router = APIRouter()
doc_generator = DocumentationGenerator()
test_generator = TestGenerator()

class CodeChangeRequest(BaseModel):
    code: str
    file_path: str
    diff: Optional[str] = None
    language: str = "python"

class TestGenerationRequest(BaseModel):
    code: str
    file_path: str
    language: str = "python"
    include_integration: bool = False

class DocumentationRequest(BaseModel):
    code: str
    file_path: str
    change_type: Optional[str] = None

@router.post("/analyze-change")
async def analyze_code_change(request: CodeChangeRequest):
    """
    Analyze code changes to determine documentation needs
    """
    try:
        diff = request.diff or request.code
        analysis = await doc_generator.analyze_code_change(diff, request.file_path)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-docs")
async def generate_documentation(request: DocumentationRequest):
    """
    Generate documentation for code changes
    """
    try:
        # Analyze the change first
        analysis = await doc_generator.analyze_code_change(request.code, request.file_path)
        
        # Generate documentation
        docs = await doc_generator.generate_documentation(
            request.code,
            request.file_path,
            analysis
        )
        
        # Route to stakeholders
        routing = await doc_generator.route_documentation(
            docs,
            [],
            analysis.get("change_type", "modification")
        )
        
        return {
            "documentation": docs,
            "analysis": analysis,
            "routing": routing
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-api-docs")
async def generate_api_documentation(request: CodeChangeRequest):
    """
    Generate API documentation from code
    """
    try:
        docs = await doc_generator.generate_api_docs(request.code, request.language)
        return {"api_documentation": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-tests")
async def generate_tests(request: TestGenerationRequest):
    """
    Generate unit tests for code
    """
    try:
        # Generate unit tests
        tests = await test_generator.generate_tests(
            request.code,
            request.file_path,
            request.language
        )
        
        # Calculate coverage
        coverage = await test_generator.calculate_coverage(request.code, tests)
        
        # Suggest additional tests
        suggestions = await test_generator.suggest_additional_tests(request.code, tests)
        
        return {
            "tests": tests,
            "coverage": coverage,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-integration-tests")
async def generate_integration_tests(
    components: List[str],
    interactions: str
):
    """
    Generate integration tests for component interactions
    """
    try:
        tests = await test_generator.generate_integration_tests(components, interactions)
        return {"integration_tests": tests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline/full")
async def full_pipeline(request: CodeChangeRequest):
    """
    Run complete documentation and test generation pipeline
    """
    try:
        # Analyze change
        analysis = await doc_generator.analyze_code_change(
            request.diff or request.code,
            request.file_path
        )
        
        # Generate documentation
        docs = await doc_generator.generate_documentation(
            request.code,
            request.file_path,
            analysis
        )
        
        # Generate tests
        tests = await test_generator.generate_tests(
            request.code,
            request.file_path,
            request.language
        )
        
        # Calculate coverage
        coverage = await test_generator.calculate_coverage(request.code, tests)
        
        # Route documentation
        routing = await doc_generator.route_documentation(
            docs,
            [],
            analysis.get("change_type", "modification")
        )
        
        return {
            "analysis": analysis,
            "documentation": docs,
            "tests": tests,
            "coverage": coverage,
            "routing": routing,
            "status": "complete"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
