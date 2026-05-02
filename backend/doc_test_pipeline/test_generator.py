"""
Test Generator
Automatically generates unit tests based on code changes
"""
import os
from typing import Dict, Any, List
from groq import Groq

class TestGenerator:
    """Generates unit tests for code changes"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    async def generate_tests(
        self,
        code: str,
        file_path: str,
        language: str = "python"
    ) -> str:
        """
        Generate unit tests for given code
        
        Args:
            code: Source code to test
            file_path: Path to source file
            language: Programming language
            
        Returns:
            Generated test code
        """
        try:
            framework = self._get_test_framework(language)
            
            prompt = f"""Generate comprehensive unit tests for this {language} code using {framework}:

File: {file_path}
Code:
```{language}
{code}
```

Generate tests that:
1. Cover all functions/methods
2. Test edge cases and error conditions
3. Include setup and teardown if needed
4. Follow {framework} best practices
5. Include docstrings explaining what each test does

Test Code:"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"# Test generation failed: {str(e)}"
    
    def _get_test_framework(self, language: str) -> str:
        """Get appropriate test framework for language"""
        frameworks = {
            "python": "pytest",
            "javascript": "Jest",
            "typescript": "Jest",
            "java": "JUnit",
            "go": "testing package",
            "ruby": "RSpec"
        }
        return frameworks.get(language.lower(), "standard testing framework")
    
    async def generate_integration_tests(
        self,
        components: List[str],
        interactions: str
    ) -> str:
        """
        Generate integration tests for component interactions
        
        Args:
            components: List of components that interact
            interactions: Description of how they interact
            
        Returns:
            Integration test code
        """
        try:
            prompt = f"""Generate integration tests for these interacting components:

Components: {', '.join(components)}
Interactions: {interactions}

Create tests that verify:
1. Component communication works correctly
2. Data flows properly between components
3. Error handling across component boundaries
4. End-to-end workflows

Integration Tests:"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"# Integration test generation failed: {str(e)}"
    
    async def calculate_coverage(
        self,
        source_code: str,
        test_code: str
    ) -> Dict[str, Any]:
        """
        Estimate test coverage
        
        Args:
            source_code: Original source code
            test_code: Generated test code
            
        Returns:
            Coverage estimation
        """
        try:
            # Simple heuristic: count functions in source vs test assertions
            import re
            
            # Count functions in source
            source_functions = len(re.findall(r'def \w+\(', source_code))
            source_classes = len(re.findall(r'class \w+', source_code))
            
            # Count test functions
            test_functions = len(re.findall(r'def test_\w+\(', test_code))
            test_assertions = len(re.findall(r'assert', test_code))
            
            # Estimate coverage
            if source_functions > 0:
                function_coverage = min(100, (test_functions / source_functions) * 100)
            else:
                function_coverage = 0
            
            return {
                "estimated_coverage": round(function_coverage, 2),
                "source_functions": source_functions,
                "source_classes": source_classes,
                "test_functions": test_functions,
                "test_assertions": test_assertions,
                "coverage_level": self._get_coverage_level(function_coverage)
            }
            
        except Exception as e:
            return {
                "estimated_coverage": 0,
                "error": str(e)
            }
    
    def _get_coverage_level(self, coverage: float) -> str:
        """Classify coverage level"""
        if coverage >= 80:
            return "excellent"
        elif coverage >= 60:
            return "good"
        elif coverage >= 40:
            return "fair"
        else:
            return "poor"
    
    async def suggest_additional_tests(
        self,
        code: str,
        existing_tests: str
    ) -> List[str]:
        """
        Suggest additional test cases that might be missing
        
        Args:
            code: Source code
            existing_tests: Current test code
            
        Returns:
            List of suggested test cases
        """
        try:
            prompt = f"""Analyze this code and existing tests to suggest additional test cases:

Source Code:
```
{code[:1000]}  # Limit to first 1000 chars
```

Existing Tests:
```
{existing_tests[:1000]}
```

Suggest 5-10 additional test cases that would improve coverage, focusing on:
1. Edge cases
2. Error conditions
3. Boundary values
4. Integration scenarios

List each suggestion as a brief description."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=800
            )
            
            # Parse suggestions from response
            suggestions = response.choices[0].message.content.split('\n')
            return [s.strip() for s in suggestions if s.strip() and len(s.strip()) > 10]
            
        except Exception as e:
            return [f"Error generating suggestions: {str(e)}"]

# Made with Bob
