#!/usr/bin/env python3
"""
LNCP LLM Expander
Version: 0.1.0

Provides LLM-assisted expansion of template content for richer, more expressive
output in Phases 2, 3, 4, and 6.

Uses Claude API when available; falls back to templates with graceful degradation notice.

Key principles:
- Non-directive: Describes patterns without prescribing changes
- Peircean frame: Uses semiotic language appropriately
- Interpretive but humble: Acknowledges sample limitations
- Forward-pointing: References future exercises and rounds
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

# Attempt to import anthropic SDK
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# =============================================================================
# Configuration
# =============================================================================

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1500

# System prompt for all LNCP expansions
LNCP_SYSTEM_PROMPT = """You are an assistant helping to generate content for LNCP (Language and Narrative Composition Project), a structural writing analysis tool.

Your role is to expand template content into richer, more expressive prose while maintaining these principles:

1. NON-DIRECTIVE: Describe what is present without prescribing what should change. Use phrases like "this pattern tends to..." rather than "you should..."

2. PEIRCEAN FRAME: Use semiotic concepts appropriately:
   - Interpretant: The meaning that forms in the reader's mind
   - Sign: The structural element that carries meaning
   - Mediation: How meaning passes through structural forms
   - Stability/Instability: How patterns resolve or remain open

3. SAMPLE-AWARE: Acknowledge that observations come from a limited sample. Use phrases like "in this sample," "with this material," "these sentences show..."

4. INTERPRETIVE BUT HUMBLE: Offer interpretations while acknowledging uncertainty. Patterns suggest rather than prove.

5. FORWARD-POINTING: Where appropriate, mention that future exercises or longer samples could reveal more.

6. HIGH-INTENT AWARENESS: When discussing modal/epistemic markers, explain how they shape the writer's stance without judging it.

7. WARM AND INVITING: The tone should feel like a thoughtful reader reflecting on writing, not a critic evaluating it.

Write in clear, flowing prose. Avoid bullet points in your expansions. Each paragraph should feel complete but connected to what comes before and after."""


# =============================================================================
# LLM Client
# =============================================================================

class LNCPExpander:
    """
    Handles LLM-assisted expansion of LNCP template content.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the expander.
        
        Args:
            api_key: Anthropic API key. If not provided, tries ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = None
        self.is_available = False
        
        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.is_available = True
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")
                self.is_available = False
    
    def expand(
        self,
        template_content: str,
        context: Dict[str, Any],
        expansion_type: str,
        target_length: str = "medium",
    ) -> Tuple[str, bool]:
        """
        Expand template content using LLM.
        
        Args:
            template_content: The base template text to expand
            context: Relevant context (metrics, prior phases, etc.)
            expansion_type: Type of expansion (e.g., "phase2_explanation", "phase3_synthesis")
            target_length: "short" (1 para), "medium" (2-3 para), "long" (3-4 para)
            
        Returns:
            (expanded_text, was_llm_enhanced)
        """
        if not self.is_available:
            return template_content, False
        
        # Build the expansion prompt
        prompt = self._build_expansion_prompt(
            template_content, context, expansion_type, target_length
        )
        
        try:
            response = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=MAX_TOKENS,
                system=LNCP_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            
            expanded = response.content[0].text
            return expanded.strip(), True
            
        except Exception as e:
            print(f"Warning: LLM expansion failed: {e}")
            return template_content, False
    
    def _build_expansion_prompt(
        self,
        template_content: str,
        context: Dict[str, Any],
        expansion_type: str,
        target_length: str,
    ) -> str:
        """Build the prompt for LLM expansion."""
        
        length_guidance = {
            "short": "Write 1 paragraph (3-5 sentences).",
            "medium": "Write 2-3 paragraphs (6-10 sentences total).",
            "long": "Write 3-4 paragraphs (10-15 sentences total).",
        }
        
        type_guidance = {
            "phase2_explanation": """
You are expanding a Phase-2 output explanation. This describes a structural metric from the writer's sample.
The explanation should:
- Start with what the metric shows in this specific sample
- Interpret what this might mean for how the writing feels or functions
- Optionally hint at what variation might look like
- Remain purely descriptive, not prescriptive
""",
            "phase3_synthesis": """
You are expanding a Phase-3 semiotic synthesis. This brings multiple outputs into relation using a Peircean lens.
The synthesis should:
- Explain the semiotic lens briefly (interpretant stabilization, mediation, or relational density)
- Show how the related outputs connect through this lens
- Offer an interpretation of what this means for the writing's effect
- Acknowledge the sample-bound nature of the observation
""",
            "phase4a_prompt": """
You are expanding a Phase-4a reflection prompt. This invites the writer to notice, reflect, rewrite, or compare.
The prompt should:
- Be inviting, not demanding
- Connect to specific observations from the analysis
- Leave room for the writer's own interpretation
- Feel like a gentle question, not an assignment
""",
            "phase4b_guidance": """
You are expanding a Phase-4b guidance item. This offers practical application insights.
The guidance should:
- Connect the structural observation to real-world writing contexts
- Offer suggestions as possibilities, not prescriptions
- Include a concrete scenario or example
- Remain warm and supportive in tone
""",
            "phase6_summary": """
You are expanding a Phase-6 summary section. This synthesizes the entire analysis.
The summary should:
- Weave together observations from multiple phases
- Provide a cohesive interpretation of the writing's structural character
- Acknowledge what a larger sample might reveal
- Point toward future exploration without being pushy
""",
            "high_intent_reflection": """
You are expanding a High-Intent reflection. This interprets the writer's use of modal/epistemic markers.
The reflection should:
- Describe the epistemic stance without judging it
- Explain how markers like "might," "certainly," "believe" shape meaning
- Connect stance to how readers might receive the writing
- Remain curious and descriptive, not evaluative
""",
        }
        
        guidance = type_guidance.get(expansion_type, "Expand this content thoughtfully.")
        length = length_guidance.get(target_length, length_guidance["medium"])
        
        # Format context as readable text
        context_text = json.dumps(context, indent=2, default=str)
        
        return f"""
{guidance}

{length}

Here is the template content to expand:
---
{template_content}
---

Here is the relevant context from the analysis:
---
{context_text}
---

Write your expanded version now. Do not include any preamble or explanation—just the expanded content itself.
"""
    
    def select_next_step(
        self,
        analysis_context: Dict[str, Any],
        prompt_pool: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], str]:
        """
        Use LLM to select the most appropriate next-step prompt.
        
        Args:
            analysis_context: Full analysis context (phase1-5 outputs, high_intent_profile)
            prompt_pool: List of available next-step prompts
            
        Returns:
            (selected_prompt, rationale)
        """
        if not self.is_available:
            # Fallback to rule-based selection
            return self._rule_based_next_step(analysis_context, prompt_pool)
        
        # Build selection prompt
        pool_text = json.dumps(prompt_pool, indent=2)
        context_text = json.dumps(analysis_context, indent=2, default=str)
        
        prompt = f"""
Based on the following analysis results, select the single most appropriate next-step prompt from the pool.

Analysis context:
{context_text}

Available prompts:
{pool_text}

Consider:
1. The writer's sample size (sentence count)
2. Their structural density and variety
3. Their epistemic stance (High-Intent profile)
4. What would be most valuable for them to explore next

Respond with ONLY a JSON object in this exact format:
{{"prompt_id": "NS_XXX", "rationale": "2-3 sentences explaining why this prompt fits"}}
"""
        
        try:
            response = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=500,
                system="You are helping select appropriate writing prompts. Respond only with valid JSON.",
                messages=[{"role": "user", "content": prompt}],
            )
            
            result_text = response.content[0].text.strip()
            # Clean potential markdown code blocks
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            prompt_id = result.get("prompt_id")
            rationale = result.get("rationale", "")
            
            # Find the selected prompt
            for p in prompt_pool:
                if p.get("prompt_id") == prompt_id:
                    return p, rationale
            
            # If not found, fall back
            return self._rule_based_next_step(analysis_context, prompt_pool)
            
        except Exception as e:
            print(f"Warning: LLM next-step selection failed: {e}")
            return self._rule_based_next_step(analysis_context, prompt_pool)
    
    def _rule_based_next_step(
        self,
        context: Dict[str, Any],
        pool: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], str]:
        """Rule-based fallback for next-step selection."""
        
        sentence_count = context.get("phase1", {}).get("outputs", {}).get("sentence_count", {}).get("count", 0)
        high_intent = context.get("high_intent_profile", {})
        
        # Simple rules
        if sentence_count < 6:
            # Low volume - suggest writing more
            for p in pool:
                if p.get("prompt_id") == "NS_001":
                    return p, f"With {sentence_count} sentences, a longer sample would reveal more patterns."
        
        # Check epistemic stance
        openness = high_intent.get("epistemic_openness", 0.5)
        if openness < 0.3:
            # Very closed stance - suggest exploring openness
            for p in pool:
                if p.get("prompt_id") == "NS_005":
                    return p, "Your writing shows a firm epistemic stance. Exploring tentativeness could expand your range."
        elif openness > 0.7:
            # Very open stance - suggest exploring certainty
            for p in pool:
                if p.get("prompt_id") == "NS_005":
                    return p, "Your writing leaves much room for interpretation. Exploring certainty could add contrast."
        
        # Default to exploration prompt
        for p in pool:
            if p.get("prompt_id") == "NS_012":
                return p, "Exploring different registers can reveal how context shapes your structural choices."
        
        # Last resort: first prompt
        return pool[0], "This prompt invites further exploration of your writing patterns."


# =============================================================================
# Singleton Instance
# =============================================================================

_expander: Optional[LNCPExpander] = None


def get_expander() -> LNCPExpander:
    """Get or create the global expander instance."""
    global _expander
    if _expander is None:
        _expander = LNCPExpander()
    return _expander


def is_llm_available() -> bool:
    """Check if LLM expansion is available."""
    return get_expander().is_available


def expand_content(
    template_content: str,
    context: Dict[str, Any],
    expansion_type: str,
    target_length: str = "medium",
) -> Tuple[str, bool]:
    """
    Convenience function to expand content.
    
    Returns:
        (expanded_text, was_llm_enhanced)
    """
    return get_expander().expand(template_content, context, expansion_type, target_length)


def select_next_step(
    analysis_context: Dict[str, Any],
    prompt_pool: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], str]:
    """
    Convenience function to select next step.
    
    Returns:
        (selected_prompt, rationale)
    """
    return get_expander().select_next_step(analysis_context, prompt_pool)


# =============================================================================
# Graceful Degradation Notice
# =============================================================================

ENHANCEMENT_NOTICE = """Enhanced analysis is available when connected to the Claude API. The current analysis uses template-based generation, which provides accurate structural insights but with less personalized interpretation. To enable enhanced analysis, configure your ANTHROPIC_API_KEY."""


def get_enhancement_notice() -> str:
    """Get the notice to show when LLM is not available."""
    return ENHANCEMENT_NOTICE


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("LNCP LLM Expander Status")
    print("=" * 40)
    print(f"Anthropic SDK available: {ANTHROPIC_AVAILABLE}")
    print(f"API key configured: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")
    
    expander = get_expander()
    print(f"LLM expansion available: {expander.is_available}")
    
    if not expander.is_available:
        print()
        print("Fallback mode active. Template content will be used.")
        print(f"Notice: {ENHANCEMENT_NOTICE[:100]}...")
