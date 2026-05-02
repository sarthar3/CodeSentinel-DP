"""
Documentation Generator
Analyzes code changes and generates appropriate documentation
"""
import os
from typing import Dict, Any, List
from groq import Groq
import re

class DocumentationGenerator:
    """Generates documentation based on code changes"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    async def analyze_code_change(self, diff: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze code changes to determine documentation needs
        
        Args:
            diff: Git diff of changes
            file_path: Path to changed file
            
        Returns:
            Analysis of what documentation is needed
        """
        try:
            prompt = f"""Analyze this code change and determine what documentation is needed:

File: {file_path}
Changes:
```
{diff}
```

Classify the change type and recommend documentation:
1. Change type: (feature, bugfix, refactor, breaking_change, config)
2. Documentation style: (api_docs, user_guide, technical_spec, changelog)
3. Affected components
4. Breaking changes (if any)

Respond in JSON format:
{{
    "change_type": "type",
    "doc_style": "style",
    "components": ["component1", "component2"],
    "breaking_changes": [],
    "summary": "brief summary"
}}"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "change_type": "unknown",
                "doc_style": "changelog",
                "components": [],
                "breaking_changes": [],
                "summary": str(e)
            }
    
    async def generate_documentation(
        self,
        code_change: str,
        file_path: str,
        change_analysis: Dict[str, Any]
    ) -> str:
        """
        Generate documentation based on code changes
        
        Args:
            code_change: The actual code changes
            file_path: Path to the file
            change_analysis: Analysis from analyze_code_change
            
        Returns:
            Generated documentation in markdown
        """
        try:
            doc_style = change_analysis.get("doc_style", "changelog")
            change_type = change_analysis.get("change_type", "unknown")
            
            prompt = f"""Generate {doc_style} documentation for this code change:

File: {file_path}
Change Type: {change_type}
Summary: {change_analysis.get('summary', '')}

Code Changes:
```
{code_change}
```

Generate clear, professional documentation that:
1. Explains what changed and why
2. Includes usage examples if it's a new feature
3. Notes any breaking changes
4. Follows markdown best practices

Documentation:"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"# Documentation Generation Failed\n\nError: {str(e)}"
    
    async def generate_api_docs(self, code: str, language: str) -> str:
        """
        Generate API documentation from code
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            API documentation
        """
        try:
            prompt = f"""Generate API documentation for this {language} code:

```{language}
{code}
```

Include:
1. Function/class descriptions
2. Parameters and return types
3. Usage examples
4. Any important notes

Format as markdown."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"# API Documentation\n\nError generating docs: {str(e)}"
    
    def classify_change_type(self, diff: str) -> str:
        """
        Classify the type of code change using NLU
        
        Args:
            diff: Git diff
            
        Returns:
            Change type classification
        """
        # Simple heuristic classification
        if "class " in diff or "def " in diff:
            if any(word in diff.lower() for word in ["new", "add", "create"]):
                return "feature"
        
        if any(word in diff.lower() for word in ["fix", "bug", "issue", "error"]):
            return "bugfix"
        
        if any(word in diff.lower() for word in ["refactor", "cleanup", "improve"]):
            return "refactor"
        
        if "breaking" in diff.lower() or "deprecated" in diff.lower():
            return "breaking_change"
        
        return "modification"
    
    async def route_documentation(
        self,
        doc_content: str,
        stakeholders: List[str],
        change_type: str
    ) -> Dict[str, Any]:
        """
        Route documentation to appropriate stakeholders
        
        Args:
            doc_content: Generated documentation
            stakeholders: List of stakeholder types
            change_type: Type of change
            
        Returns:
            Routing information
        """
        routing = {
            "feature": ["product_manager", "tech_lead", "developers"],
            "bugfix": ["qa_team", "support_team"],
            "breaking_change": ["all_teams", "management"],
            "refactor": ["tech_lead", "developers"],
            "config": ["devops", "tech_lead"]
        }
        
        recipients = routing.get(change_type, ["tech_lead"])
        
        return {
            "recipients": recipients,
            "priority": "high" if change_type == "breaking_change" else "normal",
            "channels": ["email", "slack", "jira"],
            "content": doc_content
        }

# Made with Bob
