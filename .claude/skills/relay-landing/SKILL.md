---
name: relay-landing
description: Create the Relay landing page - a distinctive, trust-building interface for the agentic governance platform. Use when building the landing page, marketing site, or trust-oriented interfaces for Relay.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Relay Landing Page Design

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:

- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

CRITICAL: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:

- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:

1. **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.

2. **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.

3. **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.

4. **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.

5. **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

IMPORTANT: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

## Relay-Specific Context

**Brand Positioning**: "DocuSign for Machine-to-Machine Reasoning" - The inevitable accountability infrastructure for autonomous agents.

**Core Message**: Autonomous agents will only operate at scale if their decisions are explainable, auditable, and defensible. Relay is the air gap between agent reasoning and execution.

**Target Audience**:
- Engineering leaders and CTOs
- AI system architects
- Compliance officers
- Technical decision-makers evaluating agent infrastructure

**Tone Requirements**:
- **Trust**: Convey security, cryptographic proof, immutability
- **Inevitability**: This isn't optional - it's infrastructure that must exist
- **Technical Sophistication**: Built for engineers, not marketers
- **Authority**: Infrastructure company (Stripe, Plaid) meets security company (1Password, Auth0)

**Visual Language Suggestions** (adapt boldly):
- Monospace typography for technical credibility
- Geometric precision with sharp angles and exact alignments
- Visual representations of signatures, seals, audit trails
- Controlled, purposeful animations (seal signing, ledger appending)
- Dark themes with strategic accent colors
- Code examples as first-class design elements

**Avoid**:
- Typical SaaS landing page templates
- Playful illustrations or mascots
- Overpromising "revolutionary" language
- Generic "AI startup" gradients and aesthetics
- Stock photos or generic 3D renders

## Key Content Sections

The landing page should include (adapt creatively):

1. **Hero**: One-sentence positioning with immediate visual impact
2. **Problem Statement**: The accountability gap in autonomous systems (e.g., "The €100K Question: Nike's agent buys from Salesforce's agent - who's accountable?")
3. **Solution**: How Relay works (deterministic policies, cryptographic seals, immutable audit trails)
4. **Visual Proof**: Show manifests, seals, audit records as design elements
5. **Integration**: Demonstrate ease of adoption (SDK integration example)
6. **Trust Signals**: Technical architecture, security guarantees
7. **CTA**: Clear call-to-action for getting started

## Technical Requirements

**Stack Flexibility**: Choose what fits the aesthetic vision (React, Vue, vanilla HTML/CSS, etc.)

**Performance Targets**:
- Fast loading (<3s time to interactive)
- Works without JavaScript (progressive enhancement)
- Mobile responsive

**Accessibility**:
- Semantic HTML
- ARIA labels for interactive elements
- Keyboard navigation
- Screen reader friendly
- Reduced motion support via `prefers-reduced-motion`

## Critical Success Factors

- [ ] Looks like critical infrastructure, not a consumer app
- [ ] Distinctive aesthetic that stands out from generic SaaS sites
- [ ] Code examples are readable, accurate, and prominent
- [ ] Animations serve functional purposes and match the brand
- [ ] Conveys trust and inevitability, not hype
- [ ] Technical credibility for engineering audiences
- [ ] Memorable visual identity

---

**Remember**: Design for the future of autonomous business. This is infrastructure that will be inevitable. Make it look and feel like it.
