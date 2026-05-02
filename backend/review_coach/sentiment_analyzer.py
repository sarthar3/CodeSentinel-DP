"""
Sentiment Analyzer for Code Reviews
Analyzes tone and sentiment of code review comments
"""
import os
from typing import Dict, Any, List
from groq import Groq
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    """Analyzes sentiment in code review comments"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using multiple methods
        
        Args:
            text: Review comment text
            
        Returns:
            Sentiment analysis results
        """
        # VADER sentiment (good for social media/informal text)
        vader_scores = self.vader.polarity_scores(text)
        
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment
        
        # Classify overall sentiment
        compound = vader_scores['compound']
        if compound >= 0.05:
            overall = "positive"
        elif compound <= -0.05:
            overall = "negative"
        else:
            overall = "neutral"
        
        # Detect specific tones
        tones = self._detect_tones(text.lower())
        
        return {
            "overall_sentiment": overall,
            "vader_scores": vader_scores,
            "polarity": textblob_sentiment.polarity,
            "subjectivity": textblob_sentiment.subjectivity,
            "tones": tones,
            "needs_improvement": overall == "negative" or "harsh" in tones
        }
    
    def _detect_tones(self, text: str) -> List[str]:
        """Detect specific tones in text"""
        tones = []
        
        # Harsh/aggressive indicators
        harsh_words = ['stupid', 'dumb', 'terrible', 'awful', 'horrible', 'wrong', 'bad']
        if any(word in text for word in harsh_words):
            tones.append("harsh")
        
        # Constructive indicators
        constructive_words = ['suggest', 'consider', 'perhaps', 'might', 'could', 'recommend']
        if any(word in text for word in constructive_words):
            tones.append("constructive")
        
        # Vague indicators
        vague_words = ['somehow', 'something', 'stuff', 'things', 'whatever']
        if any(word in text for word in vague_words):
            tones.append("vague")
        
        # Encouraging indicators
        encouraging_words = ['good', 'great', 'nice', 'excellent', 'well done']
        if any(word in text for word in encouraging_words):
            tones.append("encouraging")
        
        return tones
    
    async def improve_comment(
        self,
        original_comment: str,
        sentiment_analysis: Dict[str, Any],
        reviewer_style: str = "balanced"
    ) -> str:
        """
        Improve code review comment to be more constructive
        
        Args:
            original_comment: Original review comment
            sentiment_analysis: Sentiment analysis results
            reviewer_style: Preferred style (gentle, balanced, direct)
            
        Returns:
            Improved comment
        """
        try:
            if not sentiment_analysis.get("needs_improvement"):
                return original_comment
            
            style_guidance = {
                "gentle": "very polite and encouraging, focusing on learning opportunities",
                "balanced": "professional and constructive, balancing critique with guidance",
                "direct": "clear and straightforward while remaining respectful"
            }
            
            prompt = f"""Improve this code review comment to be more constructive and {style_guidance.get(reviewer_style, 'balanced')}:

Original Comment: "{original_comment}"

Current Issues:
- Sentiment: {sentiment_analysis.get('overall_sentiment')}
- Tones detected: {', '.join(sentiment_analysis.get('tones', []))}

Rewrite the comment to:
1. Maintain the technical feedback
2. Use constructive language
3. Provide actionable suggestions
4. Be respectful and encouraging
5. Avoid vague or harsh language

Improved Comment:"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return original_comment
    
    async def generate_review_feedback(
        self,
        code_diff: str,
        review_context: str = ""
    ) -> List[Dict[str, str]]:
        """
        Generate constructive code review feedback
        
        Args:
            code_diff: Code changes to review
            review_context: Additional context
            
        Returns:
            List of review comments
        """
        try:
            prompt = f"""Review this code change and provide constructive feedback:

Code Changes:
```
{code_diff[:2000]}  # Limit length
```

{f"Context: {review_context}" if review_context else ""}

Provide 3-5 specific, actionable review comments that:
1. Are constructive and respectful
2. Explain the "why" behind suggestions
3. Offer concrete improvements
4. Acknowledge good practices when present

Format as JSON array:
[
    {{
        "line": line_number_or_null,
        "type": "suggestion|issue|praise",
        "comment": "your comment",
        "severity": "low|medium|high"
    }}
]"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1500
            )
            
            import json
            feedback = json.loads(response.choices[0].message.content)
            
            # Analyze sentiment of each comment
            for item in feedback:
                sentiment = self.analyze_sentiment(item.get('comment', ''))
                item['sentiment'] = sentiment
            
            return feedback
            
        except Exception as e:
            return [{
                "line": None,
                "type": "error",
                "comment": f"Review generation failed: {str(e)}",
                "severity": "low"
            }]
    
    def track_reviewer_style(
        self,
        reviewer_id: str,
        comments: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze reviewer's typical style from past comments
        
        Args:
            reviewer_id: Reviewer identifier
            comments: List of past comments
            
        Returns:
            Style profile
        """
        if not comments:
            return {"style": "unknown", "avg_sentiment": 0}
        
        sentiments = []
        all_tones = []
        
        for comment in comments:
            analysis = self.analyze_sentiment(comment)
            sentiments.append(analysis['vader_scores']['compound'])
            all_tones.extend(analysis['tones'])
        
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # Determine style
        if avg_sentiment > 0.3:
            style = "encouraging"
        elif avg_sentiment < -0.1:
            style = "critical"
        else:
            style = "balanced"
        
        # Count tone frequencies
        from collections import Counter
        tone_freq = Counter(all_tones)
        
        return {
            "reviewer_id": reviewer_id,
            "style": style,
            "avg_sentiment": round(avg_sentiment, 3),
            "common_tones": dict(tone_freq.most_common(3)),
            "total_comments": len(comments)
        }

# Made with Bob
