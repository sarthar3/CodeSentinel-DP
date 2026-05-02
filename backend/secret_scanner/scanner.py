"""
Secret Scanner
Detects API keys, tokens, and secrets using entropy analysis and regex patterns
"""
import re
import math
import json
from typing import List, Dict, Tuple
from pathlib import Path
import time


class SecretScanner:
    """Scans files for potential secrets using entropy and regex"""
    
    def __init__(self):
        self.patterns = self._load_patterns()
        self.entropy_threshold = 4.5  # bits per character
        self.min_length = 20  # minimum string length to check
    
    def _load_patterns(self) -> Dict[str, str]:
        """Load regex patterns for known secret types"""
        return {
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "AWS Secret Key": r"aws(.{0,20})?['\"][0-9a-zA-Z/+]{40}['\"]",
            "GitHub Token": r"gh[pousr]_[0-9a-zA-Z]{36}",
            "Generic API Key": r"api[_-]?key['\"]?\s*[:=]\s*['\"]?([0-9a-zA-Z]{32,})['\"]?",
            "Generic Secret": r"secret['\"]?\s*[:=]\s*['\"]?([0-9a-zA-Z]{20,})['\"]?",
            "Private Key": r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----",
            "Slack Token": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
            "Stripe Key": r"sk_live_[0-9a-zA-Z]{24}",
            "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
            "Password in URL": r"[a-zA-Z]{3,10}://[^/\\s:@]{3,20}:[^/\\s:@]{3,20}@.{1,100}",
            "Generic Token": r"token['\"]?\s*[:=]\s*['\"]?([0-9a-zA-Z]{20,})['\"]?",
            "Bearer Token": r"Bearer\s+[0-9a-zA-Z\-._~+/]+=*",
            "Basic Auth": r"Basic\s+[0-9a-zA-Z+/]+=*",
            "JWT Token": r"eyJ[0-9a-zA-Z_-]*\.eyJ[0-9a-zA-Z_-]*\.[0-9a-zA-Z_-]*",
        }
    
    def calculate_entropy(self, string: str) -> float:
        """
        Calculate Shannon entropy of a string
        
        Args:
            string: String to analyze
            
        Returns:
            Entropy in bits per character
        """
        if not string:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in string:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        length = len(string)
        entropy = 0.0
        
        for count in char_counts.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def scan_line(self, line: str, line_number: int) -> List[Dict]:
        """
        Scan a single line for secrets
        
        Args:
            line: Line content
            line_number: Line number in file
            
        Returns:
            List of detected secrets
        """
        matches = []
        
        # Check regex patterns
        for secret_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, line, re.IGNORECASE):
                matched_text = match.group(0)
                
                # Calculate entropy
                entropy = self.calculate_entropy(matched_text)
                
                matches.append({
                    "line_number": line_number,
                    "secret_type": secret_type,
                    "matched_pattern": pattern,
                    "entropy": round(entropy, 2),
                    "context": line.strip()[:100],  # First 100 chars
                    "confidence": "high" if entropy > self.entropy_threshold else "medium"
                })
        
        # Check for high-entropy strings (potential secrets)
        # Look for quoted strings or assignment values
        string_patterns = [
            r'["\']([A-Za-z0-9+/=]{20,})["\']',  # Quoted strings
            r'=\s*([A-Za-z0-9+/=]{20,})(?:\s|$)',  # Assignment values
        ]
        
        for pattern in string_patterns:
            for match in re.finditer(pattern, line):
                string_value = match.group(1)
                
                if len(string_value) >= self.min_length:
                    entropy = self.calculate_entropy(string_value)
                    
                    if entropy > self.entropy_threshold:
                        matches.append({
                            "line_number": line_number,
                            "secret_type": "High Entropy String",
                            "matched_pattern": "entropy_analysis",
                            "entropy": round(entropy, 2),
                            "context": line.strip()[:100],
                            "confidence": "medium"
                        })
        
        return matches
    
    def scan_file(self, file_path: str) -> Dict:
        """
        Scan a file for secrets
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            Scan results dictionary
        """
        start_time = time.time()
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_number, line in enumerate(f, start=1):
                    line_matches = self.scan_line(line, line_number)
                    matches.extend(line_matches)
        
        except Exception as e:
            return {
                "file": file_path,
                "secrets_found": False,
                "matches": [],
                "scan_time_ms": 0,
                "error": str(e)
            }
        
        scan_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            "file": file_path,
            "secrets_found": len(matches) > 0,
            "matches": matches,
            "scan_time_ms": round(scan_time, 2)
        }
    
    def scan_directory(self, directory: str, extensions: List[str] = None) -> Dict:
        """
        Scan all files in a directory
        
        Args:
            directory: Directory path
            extensions: List of file extensions to scan (default: common code files)
            
        Returns:
            Aggregated scan results
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php', 
                         '.env', '.yml', '.yaml', '.json', '.xml', '.sh']
        
        directory_path = Path(directory)
        all_matches = []
        files_scanned = 0
        files_with_secrets = 0
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                result = self.scan_file(str(file_path))
                files_scanned += 1
                
                if result["secrets_found"]:
                    files_with_secrets += 1
                    all_matches.extend(result["matches"])
        
        return {
            "directory": directory,
            "files_scanned": files_scanned,
            "files_with_secrets": files_with_secrets,
            "total_secrets": len(all_matches),
            "matches": all_matches
        }


def main():
    """CLI entry point"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="Scan files for API keys, tokens, and secrets"
    )
    parser.add_argument(
        "path",
        help="File or directory to scan"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if secrets found (for pre-commit hooks)"
    )
    
    args = parser.parse_args()
    
    scanner = SecretScanner()
    path = Path(args.path)
    
    if path.is_file():
        result = scanner.scan_file(str(path))
    elif path.is_dir():
        result = scanner.scan_directory(str(path))
    else:
        print(f"Error: {args.path} is not a valid file or directory")
        sys.exit(1)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        if path.is_file():
            print(f"\n{'='*80}")
            print(f"Scanning: {result['file']}")
            print(f"{'='*80}")
            
            if result["secrets_found"]:
                print(f"\n⚠️  Found {len(result['matches'])} potential secret(s):\n")
                
                for match in result["matches"]:
                    print(f"Line {match['line_number']}: {match['secret_type']}")
                    print(f"  Entropy: {match['entropy']} bits/char")
                    print(f"  Confidence: {match['confidence']}")
                    print(f"  Context: {match['context']}")
                    print()
            else:
                print("\n✓ No secrets detected")
            
            print(f"Scan completed in {result['scan_time_ms']:.2f}ms")
        
        else:
            print(f"\n{'='*80}")
            print(f"Scanning directory: {result['directory']}")
            print(f"{'='*80}")
            print(f"Files scanned: {result['files_scanned']}")
            print(f"Files with secrets: {result['files_with_secrets']}")
            print(f"Total secrets found: {result['total_secrets']}")
            
            if result['total_secrets'] > 0:
                print(f"\n⚠️  Secrets detected in {result['files_with_secrets']} file(s)")
            else:
                print("\n✓ No secrets detected")
    
    # Exit with error code if secrets found and --exit-code flag is set
    if args.exit_code and (result.get("secrets_found") or result.get("total_secrets", 0) > 0):
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

# Made with Bob
