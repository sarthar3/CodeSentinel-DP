"""
Self-Healing CI/CD Healer
Parses build logs, identifies failures, and generates patches
"""
import os
import re
import json
from typing import Dict, Any, List, Optional
from groq import Groq
from ..secret_scanner.scanner import SecretScanner

class CICDHealer:
    """Analyzes CI/CD build failures and suggests patches"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.scanner = SecretScanner()
        
    async def heal_build(self, build_log: str) -> Dict[str, Any]:
        """
        Full healing pipeline: Analyze -> Patch -> Scan
        """
        try:
            # 1. Analyze failure
            analysis = await self._analyze_failure(build_log)
            
            # 2. Generate patch based on analysis
            patch_info = await self._generate_patch(analysis)
            
            # 3. Scan patch for secrets
            is_safe, findings = self.scanner.scan_text(patch_info.get("suggested_fix", ""))
            
            return {
                "analysis": analysis,
                "patch": patch_info,
                "safety": {
                    "is_safe": is_safe,
                    "findings_count": len(findings),
                    "findings": findings if findings else []
                },
                "status": "healed" if is_safe else "blocked_by_security"
            }
        except Exception as e:
            print(f"❌ Healing Pipeline Error: {str(e)}")
            raise e
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Robustly extract JSON from LLM response"""
        try:
            # Look for JSON block
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(text)
        except Exception as e:
            print(f"⚠️ JSON Parse Error: {e} | Content: {text[:100]}...")
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")

    async def _analyze_failure(self, log: str) -> Dict[str, Any]:
        """Extract error patterns and root cause from logs"""
        prompt = f"""Analyze this CI/CD build log and identify the failure. 
        You MUST respond with ONLY a valid JSON object.
        
        Log Snippet:
        {log[-4000:] if len(log) > 4000 else log}
        
        Respond in this JSON format:
        {{
            "error_message": "The primary error string",
            "error_type": "Dependency/Syntax/Test/Environment",
            "file_involved": "path/to/file.ext or None",
            "root_cause": "Detailed explanation of why it failed",
            "severity": "high/medium/low"
        }}"""
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            return self._parse_json(response.choices[0].message.content)
        except Exception as e:
            return {
                "error_message": f"Analysis failed: {str(e)}",
                "error_type": "Unknown",
                "root_cause": "System error during log analysis"
            }
            
    async def _generate_patch(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest a fix or command to resolve the failure"""
        prompt = f"""Generate a fix for this CI/CD failure.
        You MUST respond with ONLY a valid JSON object.
        
        Error: {analysis.get('error_message')}
        Type: {analysis.get('error_type')}
        Cause: {analysis.get('root_cause')}
        
        Respond in this JSON format:
        {{
            "suggested_fix": "Code snippet or CLI command to fix",
            "explanation": "Why this fix works",
            "confidence": 0.0-1.0
        }}"""
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            return self._parse_json(response.choices[0].message.content)
        except Exception as e:
            return {
                "suggested_fix": "Manual intervention required",
                "explanation": f"Patch generation failed: {str(e)}",
                "confidence": 0.0
            }

# Made with Bob
