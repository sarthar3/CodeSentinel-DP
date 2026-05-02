# ðŸ§  Transformer AI Features - CodeSentinel DP

## Overview

CodeSentinel DP now includes **dual AI engines** for the RAG ChatBot, giving you the flexibility to choose between cloud-based speed (Groq) or local deep learning (Transformers).

## ðŸš€ Dual AI Modes

### Mode 1: Groq (Default) - Lightning Fast âš¡
- **Model**: Llama 3.3 70B Versatile
- **Speed**: ~1-2 seconds response time
- **Quality**: Excellent for general queries and RAG
- **Cost**: Free tier available
- **Internet**: Required

**Best for:**
- Quick answers
- Production deployments
- High-volume queries
- When internet is available

### Mode 2: Transformers - Deep Learning ðŸ§ 
- **Models**: 
  - **DialoGPT-medium** (Microsoft) - Conversational generation
  - **BERT** (all-mpnet-base-v2) - Semantic embeddings
- **Speed**: ~5-10 seconds response time (CPU), ~2-3 seconds (GPU)
- **Quality**: Excellent for conversational context
- **Cost**: Free (runs locally)
- **Internet**: Not required after initial download

**Best for:**
- Offline environments
- Privacy-sensitive deployments
- Conversational AI with context memory
- Learning and experimentation

## ðŸ“Š Feature Comparison

| Feature | Groq Mode | Transformer Mode |
|---------|-----------|------------------|
| Response Speed | âš¡âš¡âš¡âš¡âš¡ | âš¡âš¡âš¡ |
| Conversational Memory | âŒ | âœ… |
| Offline Support | âŒ | âœ… |
| GPU Acceleration | N/A | âœ… |
| Context Window | 8K tokens | 1K tokens |
| Semantic Search | Good | Excellent |
| Setup Complexity | Easy | Moderate |

## ðŸŽ¯ Enhanced RAG Features

### 1. Better Embeddings
Upgraded from `all-MiniLM-L6-v2` to `all-mpnet-base-v2`:
- **384 dimensions** â†’ **768 dimensions**
- Better semantic understanding
- Improved relevance scoring
- More accurate document retrieval

### 2. Wikipedia Integration
Enrich your knowledge base with Wikipedia articles:

```python
# Backend API
POST /api/rag/enrich/wikipedia
{
  "topics": ["Python programming", "FastAPI", "Machine Learning"]
}
```

**Features:**
- Automatic article fetching
- Section-based chunking
- Semantic embedding
- Source attribution

### 3. Conversation Memory (Transformer Mode)
DialoGPT maintains conversation history:
- Remembers previous questions
- Contextual follow-ups
- Natural conversation flow
- Reset with `/api/rag/reset-conversation`

## ðŸ› ï¸ Installation

### Quick Install (Included in requirements.txt)
```bash
pip install torch transformers wikipedia-api sentence-transformers --upgrade
```

### Manual Install
```bash
# PyTorch (CPU version)
pip install torch>=2.11.0

# Transformers
pip install transformers>=5.7.0

# Wikipedia API
pip install wikipedia-api>=0.14.1

# Better embeddings
pip install sentence-transformers>=5.4.1
```

### GPU Support (Optional)
For faster transformer inference:
```bash
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## ðŸ“– Usage

### Frontend Toggle
1. Open RAG ChatBot
2. Look for the model toggle button in the header
3. Click to switch between:
   - ðŸš€ **Groq** (default)
   - ðŸ§  **Transformer**
4. Current model shown in badge

### API Usage

#### Query with Transformer
```bash
# Streaming
GET /api/rag/query/stream?query=your_question&use_transformer=true

# Non-streaming
POST /api/rag/query?use_transformer=true
{
  "query": "What is FastAPI?",
  "top_k": 3
}
```

#### Enrich with Wikipedia
```bash
POST /api/rag/enrich/wikipedia
{
  "topics": [
    "Software engineering",
    "Microservices",
    "REST API"
  ]
}
```

#### Reset Conversation
```bash
GET /api/rag/reset-conversation
```

#### Check Health
```bash
GET /api/rag/health

# Response
{
  "status": "healthy",
  "documents": 150,
  "transformer_available": true,
  "models": {
    "groq": "llama-3.3-70b-versatile",
    "transformer": "DialoGPT + BERT (mpnet)"
  }
}
```

## ðŸ”§ Configuration

### Environment Variables
```bash
# .env file
GROQ_API_KEY=your_groq_key_here
CHROMA_PERSIST_DIR=./backend/data/chroma
```

### Model Selection
Edit `backend/rag/transformer_engine.py`:
```python
# Change DialoGPT model size
self.dialog_model = AutoModelForCausalLM.from_pretrained(
    "microsoft/DialoGPT-small"   # Faster, less memory
    # "microsoft/DialoGPT-medium" # Balanced (default)
    # "microsoft/DialoGPT-large"  # Best quality, slower
)

# Change embedding model
self.embedding_model = SentenceTransformer(
    'all-mpnet-base-v2'           # Best quality (default)
    # 'all-MiniLM-L6-v2'          # Faster, smaller
    # 'paraphrase-multilingual'   # Multi-language support
)
```

## ðŸŽ“ Technical Details

### DialoGPT Architecture
- **Base**: GPT-2 architecture
- **Training**: 147M Reddit conversations
- **Context**: Maintains chat history
- **Generation**: Autoregressive token prediction

### BERT Embeddings
- **Model**: all-mpnet-base-v2
- **Dimensions**: 768
- **Training**: 1B+ sentence pairs
- **Use Case**: Semantic similarity search

### RAG Pipeline
```
User Query
    â†“
BERT Embedding (768-dim vector)
    â†“
ChromaDB Similarity Search
    â†“
Top-K Documents (relevance > 0.5)
    â†“
Context Building
    â†“
DialoGPT Generation (with context)
    â†“
Response with Citations
```

## ðŸ“ˆ Performance Tips

### CPU Optimization
```python
# Use smaller models
DialoGPT-small instead of medium
all-MiniLM-L6-v2 instead of mpnet

# Reduce batch size
max_length=500 instead of 1000

# Disable gradient computation
with torch.no_grad():
    # inference code
```

### GPU Acceleration
```python
# Enable GPU in transformer_engine.py
engine = TransformerRAGEngine(use_gpu=True)

# Check GPU availability
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
print(f"GPU Name: {torch.cuda.get_device_name(0)}")
```

### Memory Management
```python
# Clear cache periodically
import torch
torch.cuda.empty_cache()

# Use smaller context windows
top_k=2 instead of 3
```

## ðŸ› Troubleshooting

### Issue: "Transformer engine not available"
**Solution**: Install dependencies
```bash
pip install torch transformers wikipedia-api sentence-transformers --upgrade
```

### Issue: Slow responses on CPU
**Solution**: Use Groq mode or enable GPU
```python
# Switch to Groq in frontend
# OR install GPU-enabled PyTorch
```

### Issue: Out of memory
**Solution**: Use smaller models
```python
# DialoGPT-small instead of medium
# Reduce max_length parameter
# Close other applications
```

### Issue: Wikipedia enrichment fails
**Solution**: Check internet connection and API limits
```python
# Wikipedia API has rate limits
# Add delays between requests
time.sleep(1)
```

## ðŸ”® Future Enhancements

- [ ] Fine-tune DialoGPT on code-specific conversations
- [ ] Add GPT-4 integration option
- [ ] Support for multilingual models
- [ ] Quantization for faster inference (ONNX, TensorRT)
- [ ] Streaming token generation for transformers
- [ ] Custom embedding model training
- [ ] RAG with multiple vector stores
- [ ] Hybrid search (keyword + semantic)

## ðŸ“š References

- [DialoGPT Paper](https://arxiv.org/abs/1911.00536)
- [BERT Paper](https://arxiv.org/abs/1810.04805)
- [Sentence Transformers](https://www.sbert.net/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [PyTorch Documentation](https://pytorch.org/docs/)

## ðŸ¤ Contributing

To add new transformer models:
1. Update `backend/rag/transformer_engine.py`
2. Add model configuration
3. Update frontend toggle options
4. Test with sample queries
5. Update documentation

---

**Made with â¤ï¸ by CodeSentinel DP Team**
