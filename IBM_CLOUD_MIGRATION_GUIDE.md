# IBM Cloud Migration Guide - watsonx.ai Integration

## ðŸŽ¯ Recommended API Strategy for IBM Hackathon

Since you have **IBM Cloud access**, here's the best approach:

### Primary Recommendation: **IBM watsonx.ai**
Perfect for this hackathon! It's IBM's enterprise AI platform with:
- âœ… Multiple foundation models (Llama, Granite, Mistral, etc.)
- âœ… RAG capabilities built-in
- âœ… Code generation optimized models
- âœ… Free tier for hackathons
- âœ… IBM Cloud native integration
- âœ… Enterprise-grade security

### Alternative Options:

1. **OpenAI GPT-4** (Best overall quality)
   - Pros: Excellent quality, fast, reliable
   - Cons: Costs money (but has free trial)
   
2. **Anthropic Claude** (Best for code)
   - Pros: Great at code understanding, long context
   - Cons: Requires API key

3. **Keep Groq** (Current - Fast & Free)
   - Pros: Very fast, free tier, good quality
   - Cons: Rate limits on free tier

## ðŸš€ Migration Plan to IBM watsonx.ai

### Step 1: Get IBM Cloud Credentials

1. Log into IBM Cloud: https://cloud.ibm.com
2. Create a watsonx.ai instance
3. Get your API key and project ID
4. Note your instance URL

### Step 2: Update Environment Variables

Add to `.env`:
```env
# IBM watsonx.ai Configuration
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### Step 3: Install IBM SDK

```bash
pip install ibm-watsonx-ai ibm-watson-machine-learning
```

### Step 4: Update RAG Query Module

Replace Groq with watsonx.ai in `backend/rag/query.py`:

```python
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

class RAGQuery:
    def __init__(self):
        # Initialize watsonx.ai
        self.model = Model(
            model_id="ibm/granite-13b-chat-v2",  # or meta-llama/llama-3-70b-instruct
            credentials={
                "apikey": os.getenv("WATSONX_API_KEY"),
                "url": os.getenv("WATSONX_URL")
            },
            project_id=os.getenv("WATSONX_PROJECT_ID"),
            params={
                GenParams.MAX_NEW_TOKENS: 1000,
                GenParams.TEMPERATURE: 0.7,
                GenParams.TOP_P: 0.9,
            }
        )
    
    def query(self, query_text: str, top_k: int = 3):
        # Your existing RAG logic
        context = self._get_context(query_text, top_k)
        
        prompt = f"""Based on the following context, answer the question.
        
Context: {context}

Question: {query_text}

Answer:"""
        
        # Generate with watsonx.ai
        response = self.model.generate_text(prompt=prompt)
        return response
```

### Step 5: Update Streaming Support

For streaming responses with watsonx.ai:

```python
def query_stream(self, query_text: str, top_k: int = 3):
    context = self._get_context(query_text, top_k)
    
    prompt = f"""Based on the following context, answer the question.
    
Context: {context}

Question: {query_text}

Answer:"""
    
    # Stream tokens
    for token in self.model.generate_text_stream(prompt=prompt):
        yield token
```

## ðŸŽ¨ Benefits of IBM watsonx.ai for Hackathon

1. **IBM Native**: Shows deep IBM ecosystem integration
2. **Enterprise Ready**: Production-grade AI platform
3. **Multiple Models**: Choose best model for each task
4. **RAG Built-in**: Native support for retrieval augmented generation
5. **Governance**: Built-in AI governance and explainability
6. **Free Tier**: Generous free tier for hackathons

## ðŸ“Š Model Recommendations

### For RAG Chat:
- **ibm/granite-13b-chat-v2** - IBM's optimized chat model
- **meta-llama/llama-3-70b-instruct** - Best quality

### For Code Analysis:
- **ibm/granite-20b-code-instruct** - Optimized for code
- **codellama/codellama-34b-instruct** - Code specialist

### For General Q&A:
- **mistralai/mixtral-8x7b-instruct** - Fast and accurate
- **meta-llama/llama-3-70b-instruct** - Best overall

## ðŸ”„ Quick Migration Script

I can create a migration script that:
1. Keeps Groq as fallback
2. Uses watsonx.ai as primary
3. Automatically switches if one fails
4. Maintains all existing functionality

Would you like me to:
- [ ] Migrate to IBM watsonx.ai (Recommended for hackathon)
- [ ] Migrate to OpenAI GPT-4 (Best quality)
- [ ] Keep Groq + Add watsonx.ai as option
- [ ] Create hybrid system (watsonx.ai primary, Groq fallback)

## ðŸ’¡ My Recommendation

**For IBM Hackathon: Use IBM watsonx.ai**

Reasons:
1. Shows IBM ecosystem expertise
2. Enterprise-grade solution
3. Free for hackathon use
4. Impresses IBM judges
5. Production-ready architecture

Let me know which option you prefer, and I'll implement it!
