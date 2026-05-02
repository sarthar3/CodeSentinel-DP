"""
Root Cause Analyzer
Traces execution flow and identifies root causes of incidents
"""
import os
import re
import json
from typing import Dict, Any, List, Optional
from groq import Groq
from datetime import datetime

class RootCauseAnalyzer:
    """Analyzes incidents and traces root causes"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def _parse_json(self, text: str) -> Any:
        """Extract and parse JSON from AI response"""
        try:
            # Try parsing directly first
            return json.loads(text)
        except json.JSONDecodeError:
            # Try extracting from markdown blocks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Try finding the first { and last }
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end+1])
                except json.JSONDecodeError:
                    pass
            
            raise

    async def analyze_error_logs(self, error_logs: str) -> Dict[str, Any]:
        """
        Analyze error logs to identify patterns and root causes
        
        Args:
            error_logs: Error log content
            
        Returns:
            Analysis with root cause suggestions
        """
        try:
            # Extract key information from logs
            stack_traces = self._extract_stack_traces(error_logs)
            error_messages = self._extract_error_messages(error_logs)
            timestamps = self._extract_timestamps(error_logs)
            
            prompt = f"""Analyze these production error logs and identify the root cause:

Error Messages:
{chr(10).join(error_messages[:5])}

Stack Traces:
{chr(10).join(stack_traces[:3])}

Provide:
1. Root cause hypothesis (most likely cause)
2. Contributing factors
3. Affected components
4. Severity assessment (critical, high, medium, low)
5. Recommended immediate actions
6. Long-term fixes

Respond ONLY in JSON format:
{{
    "root_cause": "description",
    "contributing_factors": ["factor1", "factor2"],
    "affected_components": ["component1"],
    "severity": "level",
    "immediate_actions": ["action1"],
    "long_term_fixes": ["fix1"],
    "confidence": 0.0-1.0
}}"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000,
                timeout=30
            )
            
            content = response.choices[0].message.content
            analysis = self._parse_json(content)
            
            # Add extracted metadata
            analysis["metadata"] = {
                "error_count": len(error_messages),
                "stack_trace_count": len(stack_traces),
                "time_range": self._get_time_range(timestamps)
            }
            
            return analysis
            
        except Exception as e:
            return {
                "root_cause": "Analysis failed",
                "error": str(e),
                "severity": "unknown"
            }
    
    def _extract_stack_traces(self, logs: str) -> List[str]:
        """Extract stack traces from logs"""
        # Simple pattern matching for common stack trace formats
        traces = []
        lines = logs.split('\n')
        current_trace = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['traceback', 'exception', 'error', 'at ']):
                current_trace.append(line)
            elif current_trace and line.strip():
                current_trace.append(line)
            elif current_trace:
                traces.append('\n'.join(current_trace))
                current_trace = []
        
        return traces[:10]  # Limit to first 10 traces
    
    def _extract_error_messages(self, logs: str) -> List[str]:
        """Extract error messages from logs"""
        error_patterns = [
            r'ERROR:.*',
            r'Exception:.*',
            r'Error:.*',
            r'FATAL:.*',
            r'CRITICAL:.*'
        ]
        
        messages = []
        for pattern in error_patterns:
            matches = re.findall(pattern, logs, re.IGNORECASE)
            messages.extend(matches)
        
        return list(set(messages))[:20]  # Unique messages, limit to 20
    
    def _extract_timestamps(self, logs: str) -> List[str]:
        """Extract timestamps from logs"""
        # Common timestamp patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',
        ]
        
        timestamps = []
        for pattern in patterns:
            matches = re.findall(pattern, logs)
            timestamps.extend(matches)
        
        return timestamps
    
    def _get_time_range(self, timestamps: List[str]) -> Dict[str, str]:
        """Get time range from timestamps"""
        if not timestamps:
            return {"start": "unknown", "end": "unknown"}
        
        return {
            "start": timestamps[0] if timestamps else "unknown",
            "end": timestamps[-1] if timestamps else "unknown",
            "duration": f"{len(timestamps)} events"
        }
    
    async def trace_execution_flow(
        self,
        error_context: str,
        codebase_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Trace execution flow leading to error
        
        Args:
            error_context: Error information and stack trace
            codebase_context: Optional codebase context
            
        Returns:
            Execution flow trace
        """
        try:
            prompt = f"""Trace the execution flow that led to this error:

Error Context:
{error_context}

{f"Codebase Context:{codebase_context}" if codebase_context else ""}

Provide:
1. Execution flow (step by step)
2. Where the error originated
3. How it propagated
4. What conditions triggered it

Execution Flow:"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            return {
                "execution_flow": response.choices[0].message.content,
                "traced_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "execution_flow": f"Tracing failed: {str(e)}",
                "traced_at": datetime.utcnow().isoformat()
            }
    
    async def suggest_root_cause_fixes(
        self,
        root_cause: str,
        affected_components: List[str]
    ) -> List[Dict[str, str]]:
        """
        Suggest fixes for identified root cause
        
        Args:
            root_cause: Identified root cause
            affected_components: List of affected components
            
        Returns:
            List of suggested fixes with priority
        """
        try:
            prompt = f"""Suggest specific fixes for this root cause:

Root Cause: {root_cause}
Affected Components: {', '.join(affected_components)}

Provide 3-5 specific, actionable fixes with:
1. Description of the fix
2. Priority (high, medium, low)
3. Estimated effort (hours)
4. Risk level (low, medium, high)

Format as JSON array:
[
    {{
        "fix": "description",
        "priority": "level",
        "effort_hours": number,
        "risk": "level",
        "implementation_steps": ["step1", "step2"]
    }}
]"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1200
            )
            
            content = response.choices[0].message.content
            fixes = self._parse_json(content)
            return fixes
            
        except Exception as e:
            return [{
                "fix": f"Error generating fixes: {str(e)}",
                "priority": "unknown",
                "effort_hours": 0,
                "risk": "unknown"
            }]
    
    async def find_similar_incidents(
        self,
        current_incident: str,
        historical_incidents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find similar historical incidents using pattern matching
        
        Args:
            current_incident: Current incident description
            historical_incidents: List of past incidents
            
        Returns:
            Similar incidents with similarity scores
        """
        try:
            # Use AI to find semantic similarity
            incident_summaries = [
                f"{i.get('title', '')}: {i.get('description', '')[:200]}"
                for i in historical_incidents[:10]
            ]
            
            prompt = f"""Compare this current incident with historical incidents and identify similar ones:

Current Incident:
{current_incident}

Historical Incidents:
{chr(10).join([f"{i+1}. {summary}" for i, summary in enumerate(incident_summaries)])}

Return JSON array of similar incidents with similarity scores (0-1):
[
    {{
        "incident_index": number,
        "similarity_score": 0.0-1.0,
        "reason": "why similar"
    }}
]

Only include incidents with similarity > 0.5"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            similar = self._parse_json(content)
            
            # Enrich with full incident data
            enriched = []
            for match in similar:
                idx = match.get("incident_index", 0) - 1
                if 0 <= idx < len(historical_incidents):
                    enriched.append({
                        **historical_incidents[idx],
                        "similarity_score": match.get("similarity_score", 0),
                        "similarity_reason": match.get("reason", "")
                    })
            
            return enriched
            
        except Exception as e:
            return []
    
    async def generate_incident_report(
        self,
        analysis: Dict[str, Any],
        execution_flow: Dict[str, Any],
        fixes: List[Dict[str, Any]]
    ) -> str:
        """
        Generate comprehensive incident report
        
        Args:
            analysis: Root cause analysis
            execution_flow: Execution flow trace
            fixes: Suggested fixes
            
        Returns:
            Formatted incident report in markdown
        """
        # Build fixes section
        fixes_section = []
        for i, fix in enumerate(fixes):
            fix_text = f"### {i+1}. {fix.get('fix', '')}\n"
            fix_text += f"**Priority:** {fix.get('priority', 'unknown').upper()}\n"
            fix_text += f"**Effort:** {fix.get('effort_hours', 0)} hours\n"
            fix_text += f"**Risk:** {fix.get('risk', 'unknown').upper()}\n"
            fix_text += "**Steps:**\n"
            for step in fix.get('implementation_steps', []):
                fix_text += f"  - {step}\n"
            fixes_section.append(fix_text)
        
        report = f"""# Incident Analysis Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Root Cause
{analysis.get('root_cause', 'Unknown')}

**Confidence:** {analysis.get('confidence', 0) * 100:.1f}%
**Severity:** {analysis.get('severity', 'Unknown').upper()}

## Contributing Factors
{chr(10).join([f"- {factor}" for factor in analysis.get('contributing_factors', [])])}

## Affected Components
{chr(10).join([f"- {comp}" for comp in analysis.get('affected_components', [])])}

## Execution Flow
{execution_flow.get('execution_flow', 'Not available')}

## Immediate Actions Required
{chr(10).join([f"{i+1}. {action}" for i, action in enumerate(analysis.get('immediate_actions', []))])}

## Recommended Fixes

{chr(10).join(fixes_section)}

## Long-term Improvements
{chr(10).join([f"- {fix}" for fix in analysis.get('long_term_fixes', [])])}

---
*This report was generated automatically by CodeSentinel AI*
"""
        return report

# Made with Bob
