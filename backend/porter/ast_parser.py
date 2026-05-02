"""
AST Parser for Legacy Code Analysis
Uses tree-sitter for PHP, Python, and JavaScript parsing
"""
import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ASTNode:
    """Represents a parsed AST node"""
    type: str
    name: str
    start_line: int
    end_line: int
    code: str
    params: List[str] = None
    return_type: Optional[str] = None
    
    def to_dict(self):
        return {
            "type": self.type,
            "name": self.name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "code": self.code,
            "params": self.params or [],
            "return_type": self.return_type
        }


class SimplePHPParser:
    """
    Simplified PHP parser using regex patterns
    For production, use tree-sitter with proper grammar files
    """
    
    def parse(self, code: str) -> List[ASTNode]:
        """
        Parse PHP code and extract functions and classes
        
        Args:
            code: PHP source code
            
        Returns:
            List of ASTNode objects
        """
        # Strip PHP tags for easier parsing
        code = re.sub(r'<\?php', '', code, flags=re.IGNORECASE)
        code = re.sub(r'\?>', '', code, flags=re.IGNORECASE)
        
        nodes = []
        lines = code.split('\n')
        
        # Parse classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?\s*\{'
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                # Find class end (simplified - just find matching brace)
                end_line = self._find_block_end(lines, i)
                class_code = '\n'.join(lines[i:end_line+1])
                
                nodes.append(ASTNode(
                    type="class",
                    name=class_name,
                    start_line=i + 1,
                    end_line=end_line + 1,
                    code=class_code
                ))
        
        # Parse functions
        func_pattern = r'(?:public|private|protected|static)?\s*function\s+(\w+)\s*\((.*?)\)'
        for i, line in enumerate(lines):
            match = re.search(func_pattern, line)
            if match:
                func_name = match.group(1)
                params_str = match.group(2)
                
                # Parse parameters
                params = []
                if params_str.strip():
                    for param in params_str.split(','):
                        param = param.strip()
                        # Extract parameter name (remove type hints and defaults)
                        param_match = re.search(r'\$(\w+)', param)
                        if param_match:
                            params.append(param_match.group(1))
                        else:
                            # Handle non-PHP param names if any
                            params.append(param.split('=')[0].strip())
                
                # Find function end
                end_line = self._find_block_end(lines, i)
                func_code = '\n'.join(lines[i:end_line+1])
                
                nodes.append(ASTNode(
                    type="function",
                    name=func_name,
                    start_line=i + 1,
                    end_line=end_line + 1,
                    code=func_code,
                    params=params
                ))
        
        return nodes
    
    def _find_block_end(self, lines: List[str], start: int) -> int:
        """Find the end of a code block by matching braces"""
        brace_count = 0
        started = False
        
        for i in range(start, len(lines)):
            line = lines[i]
            for char in line:
                if char == '{':
                    brace_count += 1
                    started = True
                elif char == '}':
                    brace_count -= 1
                    if started and brace_count <= 0:
                        return i
        
        return len(lines) - 1


class SimpleJavaScriptParser:
    """
    Simplified JavaScript parser using regex patterns
    For production, use tree-sitter with proper grammar files
    """
    
    def parse(self, code: str) -> List[ASTNode]:
        """Parse JavaScript code and extract functions and classes"""
        nodes = []
        lines = code.split('\n')
        
        # Parse classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{'
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                end_line = self._find_block_end(lines, i)
                class_code = '\n'.join(lines[i:end_line+1])
                
                nodes.append(ASTNode(
                    type="class",
                    name=class_name,
                    start_line=i + 1,
                    end_line=end_line + 1,
                    code=class_code
                ))
        
        # Parse functions (function declarations, arrow functions, and method assignments)
        func_patterns = [
            r'function\s+([a-zA-Z_$][\w$]*)\s*\((.*?)\)',                         # function name(...)
            r'(?:const|let|var)?\s*([a-zA-Z_$][\w$]*)\s*=\s*\((.*?)\)\s*=>',      # name = (...) =>
            r'(?:const|let|var)?\s*([a-zA-Z_$][\w$]*)\s*=\s*function\s*\((.*?)\)', # name = function(...)
            r'([a-zA-Z_$][\w$]*)\s*:\s*function\s*\((.*?)\)',                     # name: function(...)
            r'([a-zA-Z_$][\w$]*)\s*\((.*?)\)\s*\{',                               # method(...) { (inside classes)
        ]
        
        for i, line in enumerate(lines):
            # Skip lines that are likely comments or noise
            if line.strip().startswith('//') or line.strip().startswith('/*'):
                continue
                
            for pattern in func_patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    params_str = match.group(2) if len(match.groups()) > 1 else ""
                    
                    # Clean up params
                    params = [p.strip().split('=')[0].strip() for p in params_str.split(',') if p.strip()]
                    
                    end_line = self._find_block_end(lines, i)
                    func_code = '\n'.join(lines[i:end_line+1])
                    
                    nodes.append(ASTNode(
                        type="function",
                        name=func_name,
                        start_line=i + 1,
                        end_line=end_line + 1,
                        code=func_code,
                        params=params
                    ))
                    break
        
        return nodes
    
    def _find_block_end(self, lines: List[str], start: int) -> int:
        """Find the end of a code block by matching braces"""
        brace_count = 0
        started = False
        
        for i in range(start, len(lines)):
            line = lines[i]
            for char in line:
                if char == '{':
                    brace_count += 1
                    started = True
                elif char == '}':
                    brace_count -= 1
                    if started and brace_count == 0:
                        return i
        
        return len(lines) - 1


class SimplePythonParser:
    """
    Simplified Python parser using regex patterns
    """
    
    def parse(self, code: str) -> List[ASTNode]:
        """Parse Python code and extract functions and classes"""
        nodes = []
        lines = code.split('\n')
        
        # Parse classes
        class_pattern = r'class\s+(\w+)(?:\(.*\))?\s*:'
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                end_line = self._find_block_end(lines, i)
                class_code = '\n'.join(lines[i:end_line+1])
                
                nodes.append(ASTNode(
                    type="class",
                    name=class_name,
                    start_line=i + 1,
                    end_line=end_line + 1,
                    code=class_code
                ))
        
        # Parse functions
        func_pattern = r'def\s+(\w+)\s*\((.*?)\)\s*(?:->\s*.*?)?\s*:'
        for i, line in enumerate(lines):
            match = re.search(func_pattern, line)
            if match:
                func_name = match.group(1)
                params_str = match.group(2)
                
                # Clean up params (handle self/cls and type hints)
                params = []
                if params_str.strip():
                    for p in params_str.split(','):
                        p = p.strip().split(':')[0].strip().split('=')[0].strip()
                        if p and p not in ['self', 'cls']:
                            params.append(p)
                
                end_line = self._find_block_end(lines, i)
                func_code = '\n'.join(lines[i:end_line+1])
                
                nodes.append(ASTNode(
                    type="function",
                    name=func_name,
                    start_line=i + 1,
                    end_line=end_line + 1,
                    code=func_code,
                    params=params
                ))
        
        return nodes
    
    def _find_block_end(self, lines: List[str], start: int) -> int:
        """Find the end of a Python block by indentation"""
        if start >= len(lines) - 1:
            return start
            
        # Get start indentation
        first_line = lines[start]
        start_indent = len(first_line) - len(first_line.lstrip())
        
        for i in range(start + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
            
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= start_indent:
                return i - 1
                
        return len(lines) - 1


class CodeParser:
    """Main parser that delegates to language-specific parsers"""
    
    def __init__(self):
        self.parsers = {
            'php': SimplePHPParser(),
            'javascript': SimpleJavaScriptParser(),
            'python': SimplePythonParser(),
        }
    
    def parse(self, code: str, language: str) -> List[ASTNode]:
        """
        Parse code in the specified language
        
        Args:
            code: Source code to parse
            language: Programming language (php, javascript, python)
            
        Returns:
            List of parsed AST nodes
        """
        parser = self.parsers.get(language.lower())
        if not parser:
            raise ValueError(f"Unsupported language: {language}")
        
        return parser.parse(code)
    
    def identify_bounded_contexts(self, nodes: List[ASTNode]) -> Dict[str, List[ASTNode]]:
        """
        Identify bounded contexts for microservice separation
        Groups related functions/classes together
        
        Args:
            nodes: List of AST nodes
            
        Returns:
            Dictionary mapping context names to node lists
        """
        contexts = {}
        
        # Simple heuristic: group by class or by function name prefix
        for node in nodes:
            if node.type == "class":
                # Each class becomes its own context
                context_name = node.name.lower()
                if context_name not in contexts:
                    contexts[context_name] = []
                contexts[context_name].append(node)
            
            elif node.type == "function":
                # Group functions by prefix (e.g., user_*, payment_*, order_*)
                parts = node.name.split('_')
                if len(parts) > 1:
                    context_name = parts[0].lower()
                else:
                    context_name = "common"
                
                if context_name not in contexts:
                    contexts[context_name] = []
                contexts[context_name].append(node)
        
        return contexts


def main():
    """CLI entry point for testing AST parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse legacy code")
    parser.add_argument("file", help="Source file to parse")
    parser.add_argument("--language", default="php", help="Programming language")
    
    args = parser.parse_args()
    
    with open(args.file, 'r') as f:
        code = f.read()
    
    code_parser = CodeParser()
    nodes = code_parser.parse(code, args.language)
    
    print(f"\nFound {len(nodes)} nodes:")
    for node in nodes:
        print(f"  {node.type}: {node.name} (lines {node.start_line}-{node.end_line})")
    
    contexts = code_parser.identify_bounded_contexts(nodes)
    print(f"\nIdentified {len(contexts)} bounded contexts:")
    for context, context_nodes in contexts.items():
        print(f"  {context}: {len(context_nodes)} nodes")


if __name__ == "__main__":
    main()

# Made with Bob
