"""
Triage Agent
Analyzes GitHub issues and assigns severity with RAG integration
"""
import os
from typing import Dict, List
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()


class TriageAgent:
    """Automated issue triage with RAG integration"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.groq_client = Groq(api_key=api_key)
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    
    def triage_issue(
        self,
        issue_title: str,
        issue_body: str,
        issue_number: int,
        similar_incidents: List[Dict] = None
    ) -> Dict:
        """
        Triage a GitHub issue
        
        Args:
            issue_title: Issue title
            issue_body: Issue description
            issue_number: Issue number
            similar_incidents: Similar incidents from RAG (optional)
            
        Returns:
            Triage result with severity, category, and recommendations
        """
        # Analyze severity
        severity = self._analyze_severity(issue_title, issue_body)
        
        # Categorize issue
        category = self._categorize_issue(issue_title, issue_body)
        
        # Identify root cause
        root_cause = self._identify_root_cause(issue_title, issue_body, similar_incidents)
        
        # Generate recommended action
        recommended_action = self._generate_recommendation(
            severity,
            category,
            root_cause,
            similar_incidents
        )
        
        # Generate reproduction steps (if applicable)
        reproduction_steps = self._generate_reproduction_steps(issue_body)
        
        return {
            "severity": severity,
            "category": category,
            "root_cause": root_cause,
            "similar_incidents": similar_incidents or [],
            "reproduction_steps": reproduction_steps,
            "recommended_action": recommended_action
        }
    
    def _analyze_severity(self, title: str, body: str) -> str:
        """Analyze issue severity using LLM"""
        
        # Keywords for quick severity detection
        critical_keywords = ['down', 'outage', 'crash', 'data loss', 'security', 'breach']
        high_keywords = ['error', 'failure', 'broken', 'not working', 'timeout']
        
        text = (title + " " + body).lower()
        
        # Quick keyword-based detection
        if any(kw in text for kw in critical_keywords):
            return "P1"
        elif any(kw in text for kw in high_keywords):
            return "P2"
        
        # Use LLM for more nuanced analysis
        try:
            prompt = f"""Analyze this GitHub issue and assign a severity level.

Title: {title}
Description: {body[:500]}

Severity Levels:
- P1 (Critical): System down, data loss, security breach, affects all users
- P2 (High): Major feature broken, affects many users, workaround exists
- P3 (Medium): Minor issue, affects few users, cosmetic issues

Respond with ONLY the severity level (P1, P2, or P3) and a brief reason in JSON format:
{{"severity": "P1/P2/P3", "reason": "brief explanation"}}"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a technical triage expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("severity", "P3")
            
        except Exception as e:
            print(f"Error in severity analysis: {e}")
            return "P3"  # Default to medium
    
    def _categorize_issue(self, title: str, body: str) -> str:
        """Categorize the issue type"""
        text = (title + " " + body).lower()
        
        categories = {
            "bug": ["bug", "error", "crash", "broken", "not working", "failure"],
            "performance": ["slow", "timeout", "performance", "latency", "memory"],
            "security": ["security", "vulnerability", "breach", "exploit", "xss", "sql injection"],
            "feature": ["feature", "enhancement", "improvement", "add"],
            "documentation": ["docs", "documentation", "readme", "guide"],
            "infrastructure": ["deploy", "ci/cd", "build", "docker", "kubernetes"]
        }
        
        for category, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return category
        
        return "other"
    
    def _identify_root_cause(
        self,
        title: str,
        body: str,
        similar_incidents: List[Dict]
    ) -> str:
        """Identify potential root cause"""
        
        # If we have similar incidents, use them for context
        if similar_incidents:
            context = "\n".join([
                f"Similar incident: {inc.get('source', 'unknown')} - {inc.get('excerpt', '')[:200]}"
                for inc in similar_incidents[:2]
            ])
        else:
            context = "No similar incidents found in knowledge base."
        
        try:
            prompt = f"""Based on this issue and similar past incidents, identify the likely root cause.

Issue Title: {title}
Issue Description: {body[:500]}

Similar Past Incidents:
{context}

Provide a concise root cause analysis (2-3 sentences):"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a technical root cause analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error in root cause analysis: {e}")
            return "Root cause analysis pending. Requires further investigation."
    
    def _generate_recommendation(
        self,
        severity: str,
        category: str,
        root_cause: str,
        similar_incidents: List[Dict]
    ) -> str:
        """Generate recommended action"""
        
        recommendations = {
            "P1": "IMMEDIATE ACTION REQUIRED: Assign to on-call engineer, create war room, notify stakeholders.",
            "P2": "HIGH PRIORITY: Assign to team lead, investigate within 4 hours, provide status update.",
            "P3": "NORMAL PRIORITY: Add to sprint backlog, assign to appropriate team member."
        }
        
        base_recommendation = recommendations.get(severity, recommendations["P3"])
        
        # Add category-specific recommendations
        if category == "security":
            base_recommendation += " Security team must review before deployment."
        elif category == "performance":
            base_recommendation += " Run performance profiling and load tests."
        elif category == "infrastructure":
            base_recommendation += " DevOps team should review infrastructure changes."
        
        # Add similar incident reference
        if similar_incidents:
            base_recommendation += f" Review {len(similar_incidents)} similar past incident(s) for context."
        
        return base_recommendation
    
    def _generate_reproduction_steps(self, body: str) -> str:
        """Extract or generate reproduction steps"""
        
        # Look for existing reproduction steps
        if "steps to reproduce" in body.lower() or "to reproduce" in body.lower():
            lines = body.split('\n')
            steps = []
            capture = False
            
            for line in lines:
                if "reproduce" in line.lower():
                    capture = True
                    continue
                if capture and line.strip():
                    if line.strip().startswith(('1.', '2.', '3.', '-', '*')):
                        steps.append(line.strip())
                    elif len(steps) > 0:
                        break
            
            if steps:
                return '\n'.join(steps)
        
        return "Reproduction steps not provided. Please add steps to reproduce the issue."


def main():
    """CLI entry point for testing triage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Triage a GitHub issue")
    parser.add_argument("--title", required=True, help="Issue title")
    parser.add_argument("--body", required=True, help="Issue body")
    parser.add_argument("--number", type=int, default=1, help="Issue number")
    
    args = parser.parse_args()
    
    agent = TriageAgent()
    result = agent.triage_issue(args.title, args.body, args.number)
    
    print("\n" + "="*80)
    print("TRIAGE RESULT")
    print("="*80)
    print(f"Severity: {result['severity']}")
    print(f"Category: {result['category']}")
    print(f"\nRoot Cause:\n{result['root_cause']}")
    print(f"\nRecommended Action:\n{result['recommended_action']}")
    print(f"\nReproduction Steps:\n{result['reproduction_steps']}")


if __name__ == "__main__":
    main()

# Made with Bob
