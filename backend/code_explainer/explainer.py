"""
Code Explainer
Translates technical code into accessible explanations
"""
import os
from typing import Dict, Any, List, Optional
from groq import Groq

class CodeExplainer:
    """Explains code in accessible language for different audiences"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    async def explain_code(
        self,
        code: str,
        audience: str = "business",
        detail_level: str = "summary"
    ) -> Dict[str, Any]:
        """
        Explain code for specific audience
        
        Args:
            code: Source code to explain
            audience: Target audience (business, executive, technical, general)
            detail_level: Level of detail (summary, detailed, deep-dive)
            
        Returns:
            Explanation tailored to audience
        """
        try:
            audience_guidance = {
                "business": "business stakeholders who need to understand what the code does and its business impact",
                "executive": "C-level executives who need high-level strategic understanding",
                "technical": "technical team members who need implementation details",
                "general": "general audience with no technical background"
            }
            
            detail_guidance = {
                "summary": "a brief 2-3 sentence overview",
                "detailed": "a comprehensive explanation with examples",
                "deep-dive": "an in-depth technical analysis"
            }
            
            prompt = f"""Explain this code for {audience_guidance.get(audience, 'general audience')}. 
Provide {detail_guidance.get(detail_level, 'a summary')}.

Code:
```
{code[:2000]}  # Limit length
```

Your explanation should:
1. Avoid technical jargon or explain it when necessary
2. Focus on what the code does and why it matters
3. Use analogies and real-world examples
4. Highlight business value and impact
5. Be clear and accessible

Explanation:"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            explanation = response.choices[0].message.content
            
            # Identify key concepts
            key_concepts = await self._extract_key_concepts(code)
            
            return {
                "explanation": explanation,
                "audience": audience,
                "detail_level": detail_level,
                "key_concepts": key_concepts
            }
            
        except Exception as e:
            return {
                "explanation": f"Unable to generate explanation: {str(e)}",
                "audience": audience,
                "detail_level": detail_level,
                "key_concepts": []
            }
    
    async def _extract_key_concepts(self, code: str) -> List[str]:
        """Extract key technical concepts from code"""
        try:
            prompt = f"""Identify 3-5 key technical concepts in this code:

```
{code[:1000]}
```

List only the concept names, one per line."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            concepts = [
                line.strip().lstrip('-•*').strip() 
                for line in response.choices[0].message.content.split('\n')
                if line.strip()
            ]
            return concepts[:5]
            
        except Exception as e:
            return []
    
    async def create_executive_summary(
        self,
        repository_analysis: Dict[str, Any],
        recent_changes: List[str]
    ) -> str:
        """
        Create executive summary of repository and changes
        
        Args:
            repository_analysis: Repository structure analysis
            recent_changes: List of recent code changes
            
        Returns:
            Executive summary in plain English
        """
        try:
            changes_text = '\n'.join(recent_changes[:5])
            
            prompt = f"""Create an executive summary for C-level stakeholders about this software project:

Repository Overview:
- Architecture: {repository_analysis.get('architecture', 'Unknown')}
- Key Components: {', '.join(repository_analysis.get('key_files', [])[:5])}

Recent Changes:
{changes_text}

Provide a 3-paragraph executive summary that:
1. Explains what the software does in business terms
2. Highlights recent improvements and their business value
3. Notes any strategic implications or risks

Use clear, non-technical language. Focus on business impact."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Unable to generate executive summary: {str(e)}"
    
    async def explain_technical_decision(
        self,
        decision: str,
        context: str,
        audience: str = "business"
    ) -> Dict[str, Any]:
        """
        Explain a technical decision in accessible terms
        
        Args:
            decision: The technical decision made
            context: Context around the decision
            audience: Target audience
            
        Returns:
            Explanation with pros, cons, and business impact
        """
        try:
            prompt = f"""Explain this technical decision for {audience} stakeholders:

Decision: {decision}
Context: {context}

Provide:
1. What was decided (in simple terms)
2. Why this decision was made
3. Benefits (business value)
4. Trade-offs or limitations
5. Impact on users/business

Use analogies and avoid jargon. Format as clear sections."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            explanation = response.choices[0].message.content
            
            return {
                "decision": decision,
                "explanation": explanation,
                "audience": audience
            }
            
        except Exception as e:
            return {
                "decision": decision,
                "explanation": f"Unable to explain decision: {str(e)}",
                "audience": audience
            }
    
    async def generate_weekly_digest(
        self,
        changes: List[Dict[str, Any]],
        metrics: Dict[str, Any]
    ) -> str:
        """
        Generate weekly digest for stakeholders
        
        Args:
            changes: List of code changes this week
            metrics: Project metrics
            
        Returns:
            Weekly digest in markdown
        """
        try:
            changes_summary = '\n'.join([
                f"- {change.get('title', 'Change')}: {change.get('description', '')[:100]}"
                for change in changes[:10]
            ])
            
            prompt = f"""Create a weekly digest for non-technical stakeholders:

This Week's Changes:
{changes_summary}

Project Metrics:
- Files changed: {metrics.get('files_changed', 0)}
- Features added: {metrics.get('features_added', 0)}
- Bugs fixed: {metrics.get('bugs_fixed', 0)}

Create a friendly, accessible weekly update that:
1. Summarizes what the team accomplished
2. Highlights business value delivered
3. Notes any important milestones
4. Keeps it positive and clear

Format as markdown with sections."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"# Weekly Digest\n\nUnable to generate digest: {str(e)}"
    
    async def translate_error_message(
        self,
        error_message: str,
        user_action: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Translate technical error into user-friendly message
        
        Args:
            error_message: Technical error message
            user_action: What the user was trying to do
            
        Returns:
            User-friendly explanation and next steps
        """
        try:
            prompt = f"""Translate this technical error into a user-friendly message:

Error: {error_message}
{f"User was trying to: {user_action}" if user_action else ""}

Provide:
1. What went wrong (in simple terms)
2. Why it happened
3. What the user should do next

Be empathetic and helpful. Avoid technical jargon."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=400
            )
            
            friendly_message = response.choices[0].message.content
            
            return {
                "original_error": error_message,
                "friendly_message": friendly_message,
                "severity": self._assess_error_severity(error_message)
            }
            
        except Exception as e:
            return {
                "original_error": error_message,
                "friendly_message": "Something went wrong. Please try again or contact support.",
                "severity": "unknown"
            }
    
    def _assess_error_severity(self, error: str) -> str:
        """Assess error severity"""
        error_lower = error.lower()
        
        if any(word in error_lower for word in ['critical', 'fatal', 'crash', 'security']):
            return "high"
        elif any(word in error_lower for word in ['error', 'failed', 'exception']):
            return "medium"
        else:
            return "low"

# Made with Bob
