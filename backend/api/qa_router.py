"""
FastAPI router for QA Agent endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List

from .schemas import QARequest, QAResponse, TestFile, CoverageReport
from ..qa_agent.generator import TestGenerator

router = APIRouter()

# Initialize test generator
test_generator = TestGenerator()


@router.post("/generate", response_model=QAResponse)
async def generate_tests(request: QARequest):
    """
    Generate tests for the provided code
    
    Args:
        request: QA request with code and language
        
    Returns:
        Generated test files and coverage report
    """
    try:
        # For demo, we'll accept code directly in code_path field
        # In production, would read from actual file path
        code = request.code_path  # Treating as code content for demo
        
        # Generate tests
        test_files_data = test_generator.generate_tests(code, request.language)
        
        if not test_files_data:
            raise HTTPException(
                status_code=400,
                detail="No tests could be generated. Please check your code."
            )
        
        # Convert to schema format
        test_files = [
            TestFile(
                filename=tf["filename"],
                content=tf["content"],
                framework=tf["framework"]
            )
            for tf in test_files_data
        ]
        
        # Calculate coverage
        coverage_data = test_generator.calculate_coverage(test_files_data)
        coverage = CoverageReport(
            total_coverage=coverage_data["total_coverage"],
            line_coverage=coverage_data["line_coverage"],
            branch_coverage=coverage_data["branch_coverage"],
            files=coverage_data["files"]
        )
        
        return QAResponse(
            test_files=test_files,
            coverage=coverage,
            tests_generated=sum(tf.get("functions_tested", 1) for tf in test_files_data)
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/analyze")
async def analyze_code(request: QARequest):
    """
    Analyze code without generating tests (just parse and count)
    
    Args:
        request: QA request with code
        
    Returns:
        Analysis results
    """
    try:
        from ..porter.ast_parser import CodeParser
        
        parser = CodeParser()
        nodes = parser.parse(request.code_path, request.language)
        
        functions = [n for n in nodes if n.type == "function"]
        classes = [n for n in nodes if n.type == "class"]
        
        return {
            "total_functions": len(functions),
            "total_classes": len(classes),
            "testable_units": len(functions) + len(classes),
            "estimated_tests": len(functions) * 2,  # 2 tests per function
            "language": request.language
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if QA Agent is ready"""
    return {
        "status": "healthy",
        "supported_languages": ["javascript", "python", "php"],
        "test_frameworks": {
            "javascript": "jest",
            "python": "pytest",
            "php": "phpunit"
        }
    }

# Made with Bob
