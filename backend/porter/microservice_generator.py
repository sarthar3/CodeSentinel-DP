"""
Microservice Generator
Generates Node.js/Express microservices from parsed AST
"""
from typing import List, Dict
from jinja2 import Template
from .ast_parser import ASTNode


class MicroserviceGenerator:
    """Generates microservices from AST nodes"""
    
    def __init__(self):
        self.service_template = self._get_service_template()
        self.dockerfile_template = self._get_dockerfile_template()
        self.openapi_template = self._get_openapi_template()
    
    def generate_microservice(
        self,
        context_name: str,
        nodes: List[ASTNode],
        source_language: str = "php"
    ) -> Dict[str, str]:
        """
        Generate a complete microservice from AST nodes
        
        Args:
            context_name: Name of the bounded context
            nodes: List of AST nodes to convert
            source_language: Source language (php, python, etc.)
            
        Returns:
            Dictionary with generated files
        """
        # Extract endpoints from nodes
        endpoints = self._extract_endpoints(nodes)
        
        # Generate service code
        service_code = self.service_template.render(
            service_name=context_name,
            endpoints=endpoints
        )
        
        # Generate Dockerfile
        dockerfile = self.dockerfile_template.render(
            service_name=context_name
        )
        
        # Generate OpenAPI spec
        openapi_spec = self._generate_openapi_spec(context_name, endpoints)
        
        # Generate package.json
        package_json = self._generate_package_json(context_name)
        
        return {
            "service_code": service_code,
            "dockerfile": dockerfile,
            "openapi_spec": openapi_spec,
            "package_json": package_json,
            "endpoints": endpoints
        }
    
    def _extract_endpoints(self, nodes: List[ASTNode]) -> List[Dict]:
        """Extract API endpoints from AST nodes"""
        endpoints = []
        
        for node in nodes:
            if node.type == "function":
                # Convert function to REST endpoint
                method = self._infer_http_method(node.name)
                path = self._generate_path(node.name)
                
                endpoints.append({
                    "name": node.name,
                    "method": method,
                    "path": path,
                    "params": node.params or [],
                    "description": f"Endpoint for {node.name}"
                })
        
        return endpoints
    
    def _infer_http_method(self, func_name: str) -> str:
        """Infer HTTP method from function name"""
        name_lower = func_name.lower()
        
        if any(prefix in name_lower for prefix in ['get', 'fetch', 'find', 'list', 'read']):
            return "GET"
        elif any(prefix in name_lower for prefix in ['create', 'add', 'insert']):
            return "POST"
        elif any(prefix in name_lower for prefix in ['update', 'edit', 'modify']):
            return "PUT"
        elif any(prefix in name_lower for prefix in ['delete', 'remove']):
            return "DELETE"
        else:
            return "POST"  # Default
    
    def _generate_path(self, func_name: str) -> str:
        """Generate REST path from function name"""
        # Convert camelCase or snake_case to kebab-case
        import re
        
        # Handle snake_case
        name = func_name.replace('_', '-')
        
        # Handle camelCase
        name = re.sub('([a-z0-9])([A-Z])', r'\1-\2', name).lower()
        
        # Remove common prefixes
        for prefix in ['get-', 'create-', 'update-', 'delete-', 'fetch-', 'find-']:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        
        return f"/{name}"
    
    def _generate_openapi_spec(self, service_name: str, endpoints: List[Dict]) -> str:
        """Generate OpenAPI 3.0 specification"""
        import json
        
        paths = {}
        for endpoint in endpoints:
            path = endpoint["path"]
            method = endpoint["method"].lower()
            
            if path not in paths:
                paths[path] = {}
            
            paths[path][method] = {
                "summary": endpoint["description"],
                "parameters": [
                    {
                        "name": param,
                        "in": "query" if method == "get" else "body",
                        "required": False,
                        "schema": {"type": "string"}
                    }
                    for param in endpoint["params"]
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{service_name.title()} Service",
                "version": "1.0.0",
                "description": f"Microservice for {service_name} operations"
            },
            "paths": paths
        }
        
        return json.dumps(spec, indent=2)
    
    def _generate_package_json(self, service_name: str) -> str:
        """Generate package.json for Node.js service"""
        import json
        
        package = {
            "name": f"{service_name}-service",
            "version": "1.0.0",
            "description": f"Microservice for {service_name}",
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "dev": "nodemon index.js"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "dotenv": "^16.3.1"
            },
            "devDependencies": {
                "nodemon": "^3.0.1"
            }
        }
        
        return json.dumps(package, indent=2)
    
    def _get_service_template(self) -> Template:
        """Get Jinja2 template for Express service"""
        template_str = """const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: '{{ service_name }}' });
});

{% for endpoint in endpoints %}
// {{ endpoint.description }}
app.{{ endpoint.method.lower() }}('{{ endpoint.path }}', async (req, res) => {
  try {
    // TODO: Implement {{ endpoint.name }} logic
    {% if endpoint.params %}
    const { {{ endpoint.params|join(', ') }} } = req.{{ 'query' if endpoint.method == 'GET' else 'body' }};
    {% endif %}
    
    // Placeholder response
    res.json({
      message: '{{ endpoint.name }} endpoint',
      {% if endpoint.params %}
      params: { {{ endpoint.params|join(', ') }} }
      {% endif %}
    });
  } catch (error) {
    console.error('Error in {{ endpoint.name }}:', error);
    res.status(500).json({ error: error.message });
  }
});

{% endfor %}

// Start server
app.listen(PORT, () => {
  console.log(`{{ service_name }} service running on port ${PORT}`);
});

module.exports = app;
"""
        return Template(template_str)
    
    def _get_dockerfile_template(self) -> Template:
        """Get Dockerfile template"""
        template_str = """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
"""
        return Template(template_str)
    
    def _get_openapi_template(self) -> Template:
        """Get OpenAPI template (not used, generated programmatically)"""
        return Template("")


def main():
    """CLI entry point for testing microservice generation"""
    import argparse
    import json
    from .ast_parser import CodeParser
    
    parser = argparse.ArgumentParser(description="Generate microservices from legacy code")
    parser.add_argument("file", help="Source file to convert")
    parser.add_argument("--language", default="php", help="Source language")
    parser.add_argument("--output", default="./output", help="Output directory")
    
    args = parser.parse_args()
    
    # Parse code
    with open(args.file, 'r') as f:
        code = f.read()
    
    code_parser = CodeParser()
    nodes = code_parser.parse(code, args.language)
    contexts = code_parser.identify_bounded_contexts(nodes)
    
    # Generate microservices
    generator = MicroserviceGenerator()
    
    for context_name, context_nodes in contexts.items():
        print(f"\nGenerating microservice for context: {context_name}")
        result = generator.generate_microservice(context_name, context_nodes, args.language)
        
        print(f"  Generated {len(result['endpoints'])} endpoints")
        print(f"  Service code: {len(result['service_code'])} bytes")
        print(f"  Dockerfile: {len(result['dockerfile'])} bytes")
        print(f"  OpenAPI spec: {len(result['openapi_spec'])} bytes")


if __name__ == "__main__":
    main()

# Made with Bob
