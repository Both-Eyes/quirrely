# LNCP Story Mode Guidelines v0.4.0

## Tone: Warm-Companion

Story Mode feels like time with a good friend—someone who notices things about your writing with genuine warmth, never judgment. Not teaching, not analyzing, just exploring together with gentle interest.

---

## Core Principles

### 1. Warmth, Not Instruction
- **Not**: "Together, let's explore what happens when..."
- **Not**: "Notice how your patterns..."
- **Yes**: "There's something lovely about how this lands."
- **Yes**: "What would happen if you tried..."

### 2. Noticing, Not Directing
- **Not**: "Write a sentence that includes..."
- **Yes**: "Sometimes the smallest details hold the most weight."
- **Yes**: "You know those moments that stay with you for no reason."

### 3. Personal Without "I"
The companion speaks warmly but never uses "I" to refer to itself.

**Allowed constructions:**
- "There's something about..." (impersonal warm)
- "You know those moments..." (gentle second-person)
- "Sometimes we remember..." (soft inclusive)
- "Notice how..." (gentle invitation)

**Not allowed:**
- "I noticed that..."
- "I wonder if..."
- "I find myself drawn to..."

### 4. Gentle Curiosity
- Pose possibilities, not instructions
- "What would happen if..." rather than "Try this..."
- Leave room for the writer to decline or diverge

---

## companion_note Field

Each Story Mode prompt includes a `companion_note`—a warm aside before the prompt itself. This sets mood and creates intimacy.

### Characteristics:
- 1-2 sentences
- Sets emotional register, not task
- Feels like something a friend might say before asking
- Never instructional
- No "I"

### Examples:

**Good:**
- "There's something about quiet moments—they stay with us longer than the loud ones."
- "You know how some details just linger? The ones that shouldn't matter but do."
- "Sometimes the smallest shift changes everything."
- "Memory keeps the strangest things."

**Not good:**
- "Today we're going to explore quiet moments." (instructional)
- "I've always loved how small details work." (uses "I")
- "This prompt will help you notice patterns." (functional, not warm)

---

## Intimacy Gradient (Progression Tags)

Story Mode progresses through levels of emotional territory, building trust naturally.

| Tag | Territory | Emotional Depth | Session Availability |
|-----|-----------|-----------------|---------------------|
| SURFACE | Observable, external | Low | Sessions 1+ |
| OBSERVATION | Noticing with mild interpretation | Low-Medium | Sessions 1+ |
| MEMORY | Personal past, lower stakes | Medium | Sessions 3+ |
| FEELING | Emotional territory | Medium-High | Sessions 5+ |
| INSIGHT | Reflective, vulnerable | High | Sessions 7+ |

### Guardrails:

1. **Slow progression**: First 2 sessions use only SURFACE and OBSERVATION
2. **Gentle boundaries**: Prompts stay boundaried ("a small moment", not "your deepest fear")
3. **Never forced**: Higher intimacy prompts are available, never required
4. **Warm framing**: companion_note always creates safety before asking

### Tag Definitions:

**SURFACE**
- External, observable reality
- No interpretation required
- Safe, grounding
- *Example*: "Something you can see from where you're sitting right now."

**OBSERVATION**
- External with mild noticing
- Light interpretation
- Slightly more personal selection
- *Example*: "A small detail that caught your attention today."

**MEMORY**
- Personal past
- Lower-stakes memories (mundane, curious)
- Not trauma territory
- *Example*: "A mundane moment you remember for no clear reason."

**FEELING**
- Emotional territory
- Internal experience
- Still boundaried (shifts, not crises)
- *Example*: "A moment when something shifted, even slightly."

**INSIGHT**
- Reflective, meaning-making
- Understanding, not confessing
- Growth-oriented
- *Example*: "Something you understand now that you didn't before."

---

## Prompt Structure

Each Story Mode prompt has:

```json
{
  "prompt_id": "STY_001",
  "mode": "STORY",
  "tags": {
    "coverage": ["NONE_EVENTS"],
    "safety": "NEUTRAL",
    "intimacy": "SURFACE"
  },
  "companion_note": "There's something about ordinary moments—they hold more than we expect.",
  "prompt_text": "Write 2–3 sentences about something you can see from where you're sitting right now."
}
```

---

## Analysis Output: Story-Specific Reflections

When analyzing Story Mode writing, Phase-6 uses narrative metaphors rather than semiotic language.

### Structural observations become narrative observations:

| Technical | Story Mode |
|-----------|------------|
| "High structural variety" | "Each sentence finds its own shape, like thoughts arriving one at a time" |
| "Short sentence length" | "Your sentences land quickly, like someone catching their breath" |
| "Parenthetical asides" | "You tuck thoughts inside thoughts—small rooms within rooms" |
| "Low density" | "Clean lines. Nothing extra. The words do the work alone." |

### Tone in analysis:

**Not**: "Your variety ratio of 0.83 indicates structural range."

**Yes**: "There's a looseness here—each sentence takes its own shape. Nothing repeats. It reads like someone thinking out loud, following where the thought goes."

---

## Comparison: School Mode vs Story Mode

| Aspect | School Mode | Story Mode |
|--------|-------------|------------|
| Tone | Collaborative-Curious | Warm-Companion |
| Voice | "Together, let's explore..." | "There's something about..." |
| Context field | `lesson_context` | `companion_note` |
| Progression | Lesson categories (BASICS→COMBINATIONS) | Intimacy gradient (SURFACE→INSIGHT) |
| Focus | Structural awareness | Narrative meaning |
| Feel | Learning partnership | Time with a good friend |
| Analysis language | Semiotic, structural | Narrative, metaphorical |

---

## Examples: Full Prompts

### SURFACE Level
```
companion_note: "Sometimes the most ordinary things are worth looking at twice."
prompt_text: "Write 2–3 sentences about something in your immediate surroundings. Keep it simple."
```

### OBSERVATION Level
```
companion_note: "You know how certain details just stay with you? The ones that probably shouldn't matter."
prompt_text: "Write 2–3 sentences about a small detail you noticed recently—something that caught your attention for reasons you can't quite explain."
```

### MEMORY Level
```
companion_note: "Memory keeps the strangest things. Not the big moments, but the odd ones."
prompt_text: "Write 2–3 sentences about a mundane moment from your past that you remember for no particular reason."
```

### FEELING Level
```
companion_note: "Sometimes something shifts, even if we can't name it right away."
prompt_text: "Write 2–3 sentences about a moment when you felt something change—even slightly."
```

### INSIGHT Level
```
companion_note: "Understanding often arrives quietly, long after the moment itself."
prompt_text: "Write 2–3 sentences about something you understand now that you didn't understand before."
```
