"""
Onboarding Assistant for Repository Analysis
Analyzes repositories and provides voice-guided onboarding
"""
import os
from typing import Dict, Any, List
from groq import Groq
from ..rag.query import RAGQueryEngine

class OnboardingAssistant:
    """Assists developers in understanding and navigating repositories"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        try:
            self.rag_engine = RAGQueryEngine()
        except Exception:
            self.rag_engine = None  # RAG not available
    
    async def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze repository structure and generate onboarding guide
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Repository analysis with key insights
        """
        try:
            # Analyze directory structure
            structure = self._analyze_structure(repo_path)
            
            # Identify key files
            key_files = self._identify_key_files(structure)
            
            # Generate architecture overview
            architecture = await self._generate_architecture_overview(key_files)
            
            return {
                "structure": structure,
                "key_files": key_files,
                "architecture": architecture,
                "entry_points": self._find_entry_points(key_files),
                "dependencies": self._analyze_dependencies(repo_path)
            }
            
        except Exception as e:
            raise Exception(f"Repository analysis failed: {str(e)}")
    
    def _analyze_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze directory structure"""
        structure = {
            "directories": [],
            "file_count": 0,
            "languages": set()
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden and common ignore directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
            
            rel_path = os.path.relpath(root, repo_path)
            if rel_path != '.':
                structure["directories"].append(rel_path)
            
            for file in files:
                structure["file_count"] += 1
                ext = os.path.splitext(file)[1]
                if ext:
                    structure["languages"].add(ext)
        
        structure["languages"] = list(structure["languages"])
        return structure
    
    def _identify_key_files(self, structure: Dict[str, Any]) -> List[str]:
        """Identify key files like README, main entry points, configs"""
        key_patterns = [
            'README.md', 'README.rst', 'README.txt',
            'main.py', 'app.py', 'index.js', 'index.ts',
            'package.json', 'requirements.txt', 'setup.py',
            'Dockerfile', 'docker-compose.yml',
            '.env.example', 'config.py', 'settings.py'
        ]
        return key_patterns
    
    def _find_entry_points(self, key_files: List[str]) -> List[str]:
        """Find application entry points"""
        entry_patterns = ['main.py', 'app.py', 'index.js', 'index.ts', 'server.js']
        return [f for f in key_files if any(pattern in f for pattern in entry_patterns)]
    
    def _analyze_dependencies(self, repo_path: str) -> Dict[str, List[str]]:
        """Analyze project dependencies"""
        dependencies = {}
        
        # Python dependencies
        req_file = os.path.join(repo_path, 'requirements.txt')
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                dependencies['python'] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Node dependencies
        package_file = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_file):
            import json
            with open(package_file, 'r') as f:
                pkg = json.load(f)
                dependencies['node'] = list(pkg.get('dependencies', {}).keys())
        
        return dependencies
    
    async def _generate_architecture_overview(self, key_files: List[str]) -> str:
        """Generate architecture overview using AI"""
        try:
            prompt = f"""Based on these key files in a repository:
{', '.join(key_files)}

Provide a brief architecture overview (2-3 sentences) describing:
1. The type of application (web app, API, library, etc.)
2. Main technology stack
3. Overall structure

Keep it concise and developer-friendly."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Unable to generate overview: {str(e)}"
    
    async def generate_onboarding_response(self, question: str, repo_context: Dict[str, Any]) -> str:
        """
        Generate contextual response to onboarding questions
        
        Args:
            question: Developer's question
            repo_context: Repository analysis context
            
        Returns:
            Detailed response with citations
        """
        try:
            # Try to get relevant documentation from RAG
            rag_answer = "No specific documentation found"
            rag_sources = []
            
            if self.rag_engine:
                try:
                    rag_results = self.rag_engine.query(question, top_k=3)
                    rag_answer = rag_results.get('answer', 'No specific documentation found')
                    rag_sources = rag_results.get('sources', [])
                except Exception:
                    pass
            
            context = f"""Repository Context:
- Architecture: {repo_context.get('architecture', 'Unknown')}
- Entry Points: {', '.join(repo_context.get('entry_points', []))}
- Key Files: {', '.join(repo_context.get('key_files', [])[:5])}

Documentation:
{rag_answer}

Sources: {', '.join([s.get('source', '') for s in rag_sources])}"""

            prompt = f"""You are an expert developer onboarding assistant. Answer this question clearly and concisely:

Question: {question}

{context}

Provide a helpful, actionable answer that helps the developer get started. Include specific file references when relevant."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I encountered an issue: {str(e)}. Please try rephrasing your question."

# Made with Bob
