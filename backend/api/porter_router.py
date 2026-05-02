"""
FastAPI router for Code Porter endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
import json

from .schemas import PorterRequest, PorterResponse, MicroserviceSpec, ASTNode
from ..porter.ast_parser import CodeParser
from ..porter.microservice_generator import MicroserviceGenerator

router = APIRouter()

# Initialize parser and generator
code_parser = CodeParser()
microservice_generator = MicroserviceGenerator()


@router.post("/analyze", response_model=PorterResponse)
async def analyze_and_generate(request: PorterRequest):
    """
    Analyze legacy code and generate microservices
    
    Args:
        request: Porter request with source code and language
        
    Returns:
        Generated microservices with AST analysis
    """
    try:
        # Validate input
        if not request.source_code or not request.source_code.strip():
            raise HTTPException(
                status_code=400,
                detail="Source code cannot be empty"
            )
        
        # Parse source code
        nodes = code_parser.parse(request.source_code, request.language)
        
        if not nodes:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"No functions or classes found in the {request.language.upper()} source code. "
                    "The Code Porter tool requires structured code (functions or classes) to identify microservice boundaries. "
                    "Please ensure your code contains valid definitions or try the 'Load Demo' button for an example."
                )
            )
        
        # Identify bounded contexts
        contexts = code_parser.identify_bounded_contexts(nodes)
        
        # Generate microservices for each context
        microservices = []
        for context_name, context_nodes in contexts.items():
            result = microservice_generator.generate_microservice(
                context_name,
                context_nodes,
                request.language
            )
            
            # Parse OpenAPI spec back to dict
            openapi_dict = json.loads(result["openapi_spec"])
            
            # Parse endpoints if it's a string
            endpoints_list = result["endpoints"]
            if isinstance(endpoints_list, str):
                try:
                    endpoints_list = json.loads(endpoints_list)
                except:
                    endpoints_list = []
            
            microservice = MicroserviceSpec(
                name=context_name,
                description=f"Microservice for {context_name} operations",
                endpoints=endpoints_list,
                dependencies=["express", "cors", "dotenv"],
                code=result["service_code"],
                dockerfile=result["dockerfile"],
                openapi_spec=openapi_dict
            )
            microservices.append(microservice)
        
        # Convert AST nodes to schema format
        ast_nodes = [
            ASTNode(
                type=node.type,
                name=node.name,
                start_line=node.start_line,
                end_line=node.end_line,
                code=node.code[:500]  # Truncate for response
            )
            for node in nodes
        ]
        
        return PorterResponse(
            microservices=microservices,
            ast_analysis=ast_nodes
        )
    
    except HTTPException:
        # Pass through expected HTTP exceptions (like 400 Bad Request)
        raise
    except ValueError as e:
        print(f"Validation error in Porter /analyze: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        print(f"UNEXPECTED ERROR IN PORTER /analyze:")
        traceback.print_exc()
        # Ensure we return a string error message
        error_msg = str(e) if str(e) else "An unexpected error occurred"
        raise HTTPException(status_code=500, detail=f"Porter internal error: {error_msg}")


@router.post("/parse")
async def parse_code(request: PorterRequest):
    """
    Parse code and return AST analysis only (no generation)
    
    Args:
        request: Porter request with source code
        
    Returns:
        AST analysis results
    """
    try:
        nodes = code_parser.parse(request.source_code, request.language)
        
        return {
            "nodes": [node.to_dict() for node in nodes],
            "count": len(nodes),
            "contexts": list(code_parser.identify_bounded_contexts(nodes).keys())
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        print(f"Validation error in Porter /parse: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        print(f"UNEXPECTED ERROR IN PORTER /parse:")
        traceback.print_exc()
        error_msg = str(e) if str(e) else "An unexpected error occurred"
        raise HTTPException(status_code=500, detail=f"Porter internal error: {error_msg}")


@router.get("/health")
async def health_check():
    """Check if Porter service is ready"""
    return {
        "status": "healthy",
        "supported_languages": ["php", "javascript", "python"]
    }

# Made with Bob
