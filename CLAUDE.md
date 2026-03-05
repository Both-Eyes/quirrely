# CLAUDE CODE SESSION MEMORY
*Last Updated: 2026-03-05*

## SYSTEM OVERVIEW

**Quirrely** is a writing voice analysis platform with three core components:
1. **LNCP Core** - Proprietary ML for writing analysis and voice detection
2. **Meta/Observers** - Real-time optimization and A/B testing intelligence  
3. **Experience Architecture** - Dynamic user progression and collaboration system

**Key Differentiator:** Self-improving ML system that gets smarter with each user interaction, designed for offline-first operation with optional cloud enhancement.

---

## DEVELOPMENT ENVIRONMENT

### SSH & Git Setup
- **Environment:** SSH connected to development server
- **Git Repository:** Connected to GitHub with deploy capabilities
- **Current Branch:** `session-seo-meta-observers`
- **Deployment:** Can deploy directly to GitHub test environment
- **Working Directory:** `/root/quirrely_v313_integrated/`

### Git Workflow
```bash
# Standard commit with Claude signature
git commit -m "$(cat <<'EOF'
feat: Description of changes

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## CORE ARCHITECTURE

### Technology Stack
- **Backend:** Python (FastAPI/Flask), PostgreSQL, Redis
- **Frontend:** TypeScript, React components
- **ML:** Custom LNCP models (local processing capable)
- **Analytics:** QStats integration, Meta/Observers optimization
- **Auth:** Custom session management, tier-based access

### Key Services
- **Word Pool Service** (`backend/word_pool_service.py`) - Usage tracking and limits
- **Collaboration Service** (`backend/collaboration_service.py`) - Partnership features
- **Conversion Triggers** (`backend/conversion_triggers.py`) - Meta/Observers integration
- **Security Middleware** (`backend/secure_auth_middleware.py`) - Auth and protection

---

## USER TIERS & WORD ALLOCATION

| Tier | Allocation | Reset Period | Features |
|------|------------|-------------|----------|
| Anonymous | 50 words | Daily | Basic analysis |
| Free | 250 words | Daily | Full analysis, progress tracking |
| Pro | 20,000 words | Monthly | Unlimited features, comparisons |
| Partnership | 10k personal + 20k shared | Monthly | Collaborative writing space |

**Note:** Authority tier was ELIMINATED - do not reintroduce.

---

## META/OBSERVERS SYSTEM

### Health Status (Current)
- **Overall Score:** 87.3/100
- **Mode:** auto_safe
- **Cycles Completed:** 247
- **Success Rate:** 89.1%

### Conversion Optimization
- **Anonymous → Signup:** 4.20% (optimizing toward 6.50%)
- **Trial → Pro:** 41.40% (optimizing toward 50%+)
- **Triggers:** 80%, 90%, 100% usage thresholds
- **A/B Testing:** 10x faster iteration vs traditional methods

---

## CURRENT USER METRICS

### Distribution
- **Total Users:** 1,847
- **Free Users:** 1,234
- **Pro Users:** 613
- **Active Sessions:** ~45 concurrent
- **New Signups/Day:** ~23

### Revenue
- **Current MRR:** $23,121
- **Avg Pro Revenue:** $37.72/month
- **Projected 1k visitors/day:** $229k MRR within 12 months

---

## RECENT MAJOR FEATURES (DEPLOYED)

### SEO & Blog Optimization
- **Blog Posts:** 40 posts with OG images and Twitter Cards
- **SEO Score:** 91/100
- **Social Sharing:** 1,247 shares with viral coefficient 0.127
- **Meta Integration:** Full social media optimization

### Collaboration System  
- **Partnership Features:** Pro tier collaborative writing
- **Word Pools:** 20k shared + 10k personal allocation per user
- **Rate Limiting:** Prevents abuse with cancellation tracking
- **UI Components:** Complete partnership dashboard and management

### Word Pool Redesign
- **New Limits:** 50/day anonymous, 250/day free, 20k/month pro
- **Conversion Triggers:** Automated optimization at usage thresholds
- **Meta Integration:** Real-time funnel optimization
- **Database:** Migration scripts and new schema deployed

---

## TESTING & DEPLOYMENT

### QStats Integration
```bash
# Test system health
./scripts/qstats_demo

# Test specific areas
./scripts/qstats_demo users
./scripts/qstats_demo meta
./scripts/qstats_demo funnel
./scripts/qstats_demo collaboration
```

### Deployment Commands
```bash
# Check status
git status

# Deploy to test environment
git add [files]
git commit -m "[commit message with Claude signature]"
# Push triggers automatic deployment to GitHub test environment
```

---

## STRATEGIC PROJECTS

### Offline-First Architecture (PLANNED)
**Goal:** Protect LNCP IP while maintaining privacy-first experience
- **Local:** Basic writing analysis, privacy protection
- **Server:** Advanced LNCP insights, author comparisons
- **Target:** Enable use in developing regions and offline environments

### Developing Regions Initiative (FUTURE)
**Vision:** Primary writing education tool for underserved communities
- **Partners:** NGOs, educational foundations, governments
- **Focus:** Sub-Saharan Africa, rural Latin America, Southeast Asia
- **Technology:** Offline-capable on basic hardware

---

## COMPETITIVE ADVANTAGES

### Technical Moats
1. **Self-Improving System:** Each user interaction improves the platform for all users
2. **Custom ML Stack:** LNCP provides unique writing voice analysis vs generic APIs
3. **Real-Time Optimization:** Meta/Observers provides 3x conversion data, 10x A/B test velocity
4. **Offline Capability:** Works without internet, unlike competitor tools

### Business Model
- **Sustainable:** Users pay for value, system improves from usage
- **Compounding:** More users = better product = more users
- **Privacy-First:** No surveillance capitalism model
- **Universal Access:** Core value available regardless of economic status

---

## DEVELOPMENT PATTERNS

### File Organization
- **Backend:** `/backend/` - Python services and APIs
- **Frontend:** `/sentense-app/src/` - React TypeScript components  
- **Scripts:** `/scripts/` - QStats and testing utilities
- **Auth:** `/auth/` - Authentication pages and flows
- **Billing:** `/billing/` - Upgrade and payment flows

### Code Conventions
- Always check existing patterns before implementing
- Use existing libraries and utilities
- Follow TypeScript types strictly
- Never add comments unless explicitly requested
- Maintain security best practices (no secrets in code)

---

## CRITICAL CONTEXT FOR NEW SESSIONS

### What NOT to do:
- **Never reintroduce authority tier** - it was eliminated intentionally
- **Never assume libraries are available** - always check existing dependencies
- **Never commit without explicit user request**
- **Never create documentation files proactively** - only when requested

### What TO do:
- Use TodoWrite tool for complex tasks
- Check QStats for system health before major changes
- Follow existing code patterns and conventions
- Use parallel tool calls for efficiency
- Update this CLAUDE.md file when major changes are made

### Common Commands
```bash
# Quick system check
./scripts/qstats_demo | head -20

# Check recent changes  
git log --oneline -5

# See current uncommitted work
git status

# Test collaboration features
python3 test_collaboration_suite.py
```

---

## SESSION CONTINUITY CHECKLIST

When starting a new session, review:
1. Current git branch and recent commits
2. QStats system health status
3. Any uncommitted changes needing attention
4. Recent todos or project status
5. This CLAUDE.md file for context

**Remember:** We can deploy to GitHub test environment directly. Always verify system health with QStats before and after major changes.