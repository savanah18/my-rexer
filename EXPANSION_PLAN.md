# my-rxer Expansion Plan

> **Version**: 1.0  
> **Created by**: Deep Agent Code (dcode) with Qwen3.5-9B (4-bit AWQ via vLLM)  
> **Date**: 2024

---

## Executive Summary

my-rxer is currently at **~15% maturity** on its path to becoming a fully-featured multi-agent AI research system. This plan outlines the strategy to transform it from a foundational scaffold into a production-ready knowledge synthesis and AI research tool.

**Key Decisions:**
- **Architecture**: Hybrid modular with 3-tier design (Agents → Skills → Tools)
- **Final State**: 5+ distinct autonomous agents that collaborate on complex tasks
- **Timeline**: 150-250 hours to reach near-production quality (Phases P0-P4)
- **Priority**: Build iteratively, validate each feature with real use cases

---

## Current State Assessment

### What Exists (15% Complete)

```
my-rxer/
├── methods/              # Empty - needs research methodologies
├── src/deepagent/        # ~20% complete - basic worker/registry hooks
├── webagents/spiders/    # Partial - search/scraping prototypes
├── www/researcher/       # ~20% complete - framework scaffold + 2 skills
├── skills/               # Prototypes only - search & knowledge skills
└── .deepagents/rules/    # Basic rules defined
```

**Foundational Components:**
- ✅ NPM project structure initialized
- ✅ Basic worker class and registry skeleton
- ✅ Deepagent rules and governance layer
- ✅ Research agent basic framework
- ✅ Simple skill prototypes (search, knowledge)

**Missing/Core Components:**
- ❌ vLLM client integration (no working LLM interface)
- ❌ Skill composition engine (skills cannot work together)
- ❌ Agent communication/bus system
- ❌ Memory/persistence layer
- ❌ Task scheduling and parallel execution
- ❌ Critical agents (planner, writer, critic, scheduler)
- ❌ Complex workflows and error handling
- ❌ Monitoring/logging infrastructure

### Current Capabilities

| Feature | Status | Notes |
|---------|--------|-------|
| Single-task research | 🟡 Limited | Can search but no synthesis pipeline |
| Multi-skill usage | ❌ No | Skills isolated, no composition |
| Parallel execution | ❌ No | Single-threaded only |
| Self-correction | ❌ No | No validation/critique mechanism |
| Knowledge persistence | ❌ No | In-memory only, no storage |

---

## Target State (95% Complete)

```
my-rxer/
├── agents/               # 5 distinct autonomous agents
│   ├── planner/          # Breaks tasks into subtasks
│   ├── researcher/       # Multi-source data gathering
│   ├── writer/           # Synthesizes outputs
│   ├── critic/           # Validates and critiques work
│   └── scheduler/        # Orchestrates parallel execution
├── skills/              # 10+ re-composable skill modules
│   ├── search/          # Multi-engine, multi-format search
│   ├── extractor/       # Scrape, parse, summarize
│   ├── synthesizer/      # Cross-source synthesis
│   ├── analyzer/        | Pattern/quality detection
│   ├── knowledge/       | Graph/persistent knowledge base
│   └── ...              # More specialized skills
├── tools/               # 8+ reusable tool abstractions
│   ├── llm/             | vLLM client with prompt templates
│   ├── web/             | API hooks, parsers, scrapers
│   ├── file/            | Read/write, structured storage
│   ├── memory/          | Short/long-term + persistent store
│   └── ...              | Specialized tools
├── core/                # Agent framework and infrastructure
│   ├── engine/          | Agent lifecycle management
│   ├── registry/        | Skill/tools registration
│   ├── scheduler/       | Task queue + parallel execution
│   └── monitor/         | Logging, metrics, tracing
├── tests/               | Comprehensive test suite
└── config/              | Agent configs, rules, presets
```

**Capabilities to Add:**

| Feature | Status | Essential Capabilities |
|---------|--------|-------------------------|
| Multi-agent collaboration | 🟢 Planned | Planner delegates → Researcher gathers → Writer synthesizes → Critic validates |
| Skill composition | 🟢 Planned | Any skill can be used by any agent |
| Parallel execution | 🟢 Planned | Multiple agents/tasks run simultaneously |
| Self-correction | 🟢 Planned | Critic agent validates output, requests revisions |
| Knowledge persistence | 🟢 Planned | Save research results to disk/graph DB |
| Monitoring & config | 🟢 Planned | Configurable agents, metrics, logging |

---

## Proposed Architecture

### Governance Layer

```
┌─────────────────────────────────────────────┐
│           Deep Agent Code (dcode)           │
│    Rules & Master Governance Configuration  │
└─────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│              Agent Lifecycle                 │
│         (Instantiate → Execute → Clean)     │
└─────────────────────────────────────────────┘
```

### 3-Tier Model

```
┌─────────────────────────────────────────────────────────┐
│                    TIER 3: AGENTS                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Planner  │ │ Researcher│ │ Writer   │ │ Critic   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│                  Scheduler (orchestrates all)            │
├─────────────────────────────────────────────────────────┤
│                    TIER 2: SKILLS                       │
│  Search │ Extract │ Synthesize │ Analyze │ Critique     │
│  Graph  │ Parse   │ Summarize │ Validate│ Quality       │
├─────────────────────────────────────────────────────────┤
│                    TIER 1: TOOLS                        │
│  LLM │ Web │ File │ Memory │ API │ Cache │ Log         │
└─────────────────────────────────────────────────────────┘
```

**Interaction Pattern:**
```
User Prompt
    ↓
Plan er (decomposes) → Subtasks
    ↓
Scheduler (queues) → Multiple agents in parallel
    ↓
Each Agent → Uses Skills → Uses Tools
    ↓
Critic (validates each output) → Rejects if needed
    ↓
Writer (combines validated results) → Final Output
    ↓
User receives result + memory persisted
```

---

## Detailed Use Case Descriptions

### Use Case 1: Autonomous AI Research

**Description:**
User asks "Research the current state of RAG (Retrieval-Augmented Generation) architectures" → System autonomously searches multiple sources (arXiv, academic papers, technical blogs, GitHub repos) → Synthesizes findings → Delivers structured report.

**Workflow:**
```
1. Planner: Identify subtasks (search papers, search blogs, find repos)
2. Researcher: Execute subtasks in parallel using Search skill
3. Researcher: Extract and organize data using Extract skill
4. Synthesizer: Combine findings using Synthesize skill
5. Writer: Format as report
6. Critic: Validate completeness, accuracy, citations
7. Writer (revise): Incorporate critique feedback
8. Scheduler: Deliver final report
```

**Acceptance Criteria:**
- [ ] Searches 3+ distinct source types
- [ ] Creates structured summary with citations
- [ ] Validates facts against multiple sources
- [ ] Delivers within 5 minutes for typical queries
- [ ] Works without human intervention

**Complexity:** High  
**Effort:** P1 (Core)  
**Estimate:** 40-60 hours

---

### Use Case 2: Cross-Capabilities Analysis

**Description:**
User provides a topic ("Image captioning in vision-language models") → System finds 5+ different methods/approaches → Compares them on accuracy, efficiency, scalability → Recommends best for specific use case.

**Workflow:**
```
1. Planner: Identify comparison dimensions (accuracy, efficiency, complexity)
2. Researcher: Find 5+ distinct approaches
3. Analyzer: Evaluate each against criteria
4. Synthesizer: Create comparison matrix
5. Writer: Generate recommendation report
6. Critic: Validate logic of comparisons
```

**Acceptance Criteria:**
- [ ] Identifies at least 5 different methods
- [ ] Creates comparison table/list
- [ ] Provides objective scoring for each
- [ ] Includes pros/cons for each
- [ ] Recommends specific use cases for each approach

**Complexity:** Medium-High  
**Effort:** P1  
**Estimate:** 40-80 hours

---

### Use Case 3: Interactive Learning Agent

**Description:**
User provides a concept ("Explain transformers to me like I'm 12") → System explains concept using multiple analogies, multiple depths, multiple perspectives → Adjusts based on follow-up questions.

**Workflow:**
```
1. Planner: Determine explanation depth, analogies, examples
2. Writer: Create explanation at multiple levels
3. Memory: Track user's prior knowledge
4. Researcher: Find current analogies/frameworks used
5. Writer: Synthesize explanation
6. Critic: Validate for accuracy & accessibility
```

**Acceptance Criteria:**
- [ ] Provides explanation at 2+ complexity levels
- [ ] Uses at least 2 distinct analogies
- [ ] Includes concrete examples
- [ ] Answers follow-up questions based on prior context
- [ ] Adjusts explanation based on user feedback

**Complexity:** Medium  
**Effort:** P2  
**Estimate:** 50-70 hours

---

### Use Case 4: Knowledge Base Curation

**Description:**
User provides 100+ AI research papers (PDFs) → System reads all papers → Builds structured knowledge graph → Generates next-papers-to-read recommendations → Identifies emerging themes.

**Workflow:**
```
1. Planner: Map processing pipeline (extract metadata,正文, citations)
2. Researcher: Process each paper using Extract skill
3. Knowledge: Store in structured format (graph DB or semantic index)
4. Analyzer: Find connections, gaps, trends
5. Synthesizer: Create summary and recommendations
6. Writer: Output structured report
```

**Acceptance Criteria:**
- [ ] Processes 50+ papers in batch
- [ ] Creates searchable knowledge index
- [ ] Generates 5-10 recommendations per 100 papers
- [ ] Identifies at least 3 emerging themes
- [ ] Can be re-run on new papers

**Complexity:** High  
**Effort:** P2  
**Estimate:** 60-100 hours

---

### Use Case 5: Competitive Monitoring

**Description:**
User subscribes to "Deviations in multi-modal learning" → System scans arXiv, Google Scholar, Twitter/X, HuggingFace, tech blogs weekly → Alerts on relevant breakthroughs → Summarizes weekly.

**Workflow:**
```
1. Scheduler: Weekly task trigger
2. Researcher: Search all configured sources
3. Analyzer: Filter by relevance score
4. Memory: Update knowledge of new topics
5. Writer: Weekly digest
6. Critic: Validate false positives
```

**Acceptance Criteria:**
- [ ] Scans 3+ sources weekly
- [ ] Alerts within 24 hours of discovery
- [ ] Can be configured for specific keywords/tags
- [ ] Provides context for each alert
- [ ] Maintains persistent feed across runs

**Complexity:** Medium  
**Effort:** P2  
**Estimate:** 50-80 hours

---

### Use Case 6: Batch Research (Multi-Task)

**Description:**
User asks "Research 3 AI topics in parallel: 1) Long-context models, 2) AI safety, 3) Multimodal reasoning" → System runs 3 research campaigns simultaneously, then synthesizes cross-topic insights.

**Workflow:**
```
1. Planner: Create 3 independent research threads
2. Scheduler: Launch all 3 in parallel
3. Monitor: Track progress and ensure no overlap
4. Researcher: Each run via Researcher agent
5. Synthesizer: Combine insights, find connections
6. Critic: Validate both independence and synthesis
```

**Acceptance Criteria:**
- [ ] Execute 3+ tasks in parallel within time limit
- [ ] No task interference or race conditions
- [ ] Synthesizes cross-topic connections
- [ ] Reports any conflicts/contradictions
- [ ] Individual reports + combined wrap-up

**Complexity:** Medium-High  
**Effort:** P2-P3  
**Estimate:** 80-120 hours

---

### Use Case 7: Self-Correcting Research

**Description:**
User asks "What is the current state of LLM inference optimization?" → System researches → Critic identifies gaps → Researcher fills gaps → Repeat 2-3 times → Final highly validated report.

**Workflow:**
```
Round 1:
1. Researcher: Initial broad search
2. Writer: First draft
3. Critic: Identifies gaps (e.g., missing recent papers)
4. Planner: Create follow-up task for specific gaps

Round 2:
5. Researcher: Targeted search for gaps
6. Write r: Update with new findings
7. Critic: Second validation

Round 3 + Final:
8. Writer: Polished report
9. Critic: Final validation
10. Scholar: Deliver
```

**Acceptance Criteria:**
- [ ] Identifies missing components in first pass
- [ ] Iterates up to 3 correction cycles
- [ ] Improves quality measurably each cycle
- [ ] Logs correction history
- [ ] Final output passes quality check

**Complexity:** High  
**Effort:** P3  
**Estimate:** 60-120 hours

---

## Skills & Methods Organization

### Skills Structure

```
my-rxer/www/researcher/skills/
├── README.md
├── search-skill.md
├── knowledge-skill.md
├── extract-skill.md           # Parse, scrape, summarize
├── synthesize-skill.md         | Combine multi-source excerpts
├── analyze-skill.md            | Pattern/quality detection
├── critic-skill.md             | Validate, fact-check
├── format-skill.md             | Template-based output
└── ...                        # More specialized as needed
```

**Skill Characteristics:**
- ✅ **Atomic**: Single responsibility, composable
- ✅ **Testable**: Unit test each skill independently
- ✅ **Documented**: Clear inputs/outputs, parameters
- ✅ **Reusable**: Used by multiple agents

### Methods Structure

```
my-rxer/methods/
├── README.md
├── research-methodology.md     # How research agents work
├── comparison-framework.md     | Structured comparison approach
├── synthesis-strategy.md       | Merging multiple sources
├── validation-framework.md     | Quality assurance patterns
├── documentation-patterns.md   | Output formatting
└── ...
```

### Skill Integration

Each agent uses specific skill combinations:

| Agent | Skills Used |
|-------|-------------|
| Planner | analyze, format |
| Researcher | search, extract, analyze |
| Writer | extract, synthesize, format |
| Critic | analyze, critic, validate |
| Scheduler | All (orchestrates) |

---

## Implementation Phases

### Phase P0: Core Foundation (40-60 hours)

**Goal:** Establish infra structure for all future agents

| Feature | Description | Effort |
|---------|-------------|--------|
| Worker base class | Register, instantiate, execute | 8h |
| Tool abstraction | LLM, web, file, memory | 12h |
| vLLM client wrapper | Prompt templates, streaming | 10h |
| Skill registry | Register, instantiate, execute | 8h |
| Basic test runner | Unit tests for components | 8h |
| Config system | Load configs, environment vars | 8h |
| Logging/monitoring | Structured logs, metrics | 6h |

**Acceptance Criteria for P0:**
- [ ] Can load vLLM, bb query prompts
- [ ] Can instantiate any skill/tool
- [ ] Can register 3+ agents concurrently
- [ ] Can run tests and get coverage

---

### Phase P1: Core Agents (40-80 hours)

**Goal:** Working single-agent research system

| Feature | Description | Effort |
|---------|-------------|--------|
| Planner agent | Decompose tasks into subtasks | 12h |
| Researcher agent | Multi-source data gathering | 15h |
| Synthesizer skill | Cross-source synthesis | 15h |
| Writer agent | Format structured output | 10h |
| Basic critic agent | Validate, flag issues | 8h |
| Integration tests | End-to-end P1 workflows | 10h |

**Acceptance Criteria for P1:**
- [ ] Can execute full research workflow
- [ ] Delivers synthesized reports (not just raw data)
- [ ] Uses 3+ sources per research task
- [ ] Basic validation via critic agent

---

### Phase P2: Multi-Agent Communication (50-100 hours)

**Goal:** Multiple agents working together

| Feature | Description | Effort |
|---------|-------------|--------|
| Event bus/communication | Agents signal to each other | 15h |
| Task delegation system | Planner→Researcher handoff | 12h |
| Scheduler agent | Queue, parallel execution | 15h |
| Monitor agent | Track all agents, handle failures | 10h |
| Intermediate tests | Multi-agent interactions | 10h |

**Acceptance Criteria for P2:**
- [ ] Planner can delegate to Researcher
- [ ] Researcher can handoff to Writer
- [ ] Scheduler runs tasks in parallel
- [ ] Can execute Use Case 6 (batch research)

---

### Phase P3: Advanced Workflows (60-120 hours)

**Goal:** Complex self-correcting, persistent research

| Feature | Description | Effort |
|---------|-------------|--------|
| Memory persistence | Save, load, update results | 15h |
| Self-correction loop | Auto-iterate on critic flags | 15h |
| Knowledge graph | Store research as graph | 20h |
| Advanced critic | Deep validation, cross-checking | 20h |
| Recommendation engine | Suggest follow-up topics | 10h |

**Acceptance Criteria for P3:**
- [ ] Can execute Use Case 4 (curate papers)
- [ ] Can execute Use Case 7 (self-correcting)
- [ ] Results persist to disk/graph DB
- [ ] Recommends related future topics

---

### Phase P4: Production Readiness (60-80 hours)

**Goal:** Enterprise-grade monitoring, config, deployment

| Feature | Description | Effort |
|---------|-------------|--------|
| Monitoring dashboard | Visual status, metrics | 15h |
| Alert system | Notifications, alerts | 10h |
| CLI/HTTP API interface | External control | 15h |
| Deployment config | Docker, deploy to cloud | 10h |
| Error handling/guardrails | Robust failure recovery | 10h |
| Docs & tutorials | Usage guides, examples | 10h |

**Acceptance Criteria for P4:**
- [ ] Can be deployed on cloud infrastructure
- [ ] Can be controlled via API
- [ ] Has visual monitoring interface
- [ ] Handles failures gracefully
- [ ] Documentation complete

---

## Technical Recommendations

### Infrastructure Stack

| Component | Recommended | Why |
|-----------|-------------|-----|
| **LLM Backend** | vLLM (local) | Open weights, no subscription cost, 4-bit AWQ efficiency |
| **Memory (Short-term)** | In-memory Dict | Fast, simple, sufficient for task duration |
| **Memory (Long-term)** | SQLite or Vector DB | Persist research outcomes, enable search |
| **Knowledge Graph** | NetworkX or Neo4j | Store relationships, enable graph queries |
| **Task Queue** | asyncio.Queue | Native async, no external dependency |
| **Event Bus** | asyncio.Queue + Dict | Simple signal propagation |
| **Monitoring** | Prometheus + Grafana | Industry standard, rich visualization |
| **Deployment** | Docker + Docker Compose | Isolated, reproducible, easy to deploy |
| **Testing** | pytest + coverage | Standard unit/integration testing |

### Code Organization

```
my-rxer/
├── agents/                 # Agent implementations
├── skills/                 # Reusable skills
├── tools/                  # Tools (LLM, web, etc.)
├── core/                   | Core infrastructure
├── tests/                  | Comprehensive test suite
├── config/                 | Configuration files
├── docs/                   | Documentation
└── scripts/                | Utility scripts
```

### Key Engineering Decisions

1. **Async-first**: Use `async/await` throughout for performance
2. **TypeScript**: Optional but recommended for type-safety
3. **Modular**: Each component works independently for testing
4. **Configured**: All behavior configurable, versioned
5. **Testable**: Unit tests for all core functions

---

## Timeline Summary

### Total Effort to P4
- **150-250 hours** hands-on development time

### Time Distribution

| Phase | Hours | % Complete |
|-------|-------|------------|
| P0 | 40-60 | ~6-10% |
| P1 | 40-80 | ~12-20% |
| P2 | 50-100 | ~17-33% |
| P3 | 60-120 | ~23-47% |
| P4 | 60-80 | ~29-48% |

### Realistic Timeline

| Scenario | Timeline to P1 (Usable) | Timeline to P4 (Production) |
|----------|-------------------------|-----------------------------|
| Full-time (40h/day) | 1-2 weeks | 1.5-2 months |
| Part-time (20h/day) | 2-4 weeks | 3-6 months |
| Weekend only (8h) | 8-14 weeks | 6-10 months |

---

## Decision Log

### Key Architectural Decisions

1. **Go with Multi-Agent**: Single agent is useful but limited. Multiple agents with specialization provides explosion of capability.

2. **Modular over Monolithic**: Each agent/skill/tool should be independently testable and composable.

3. **Async-first**: Research will be I/O bound (LLM calls, web requests). Async is natural fit.

4. **Start P0 immediately**: Without solid foundation, can't build agents or skills.

5. **Iterative validation**: Don't build in isolation. Validate P0 with minimal viable agent, then expand.

### Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep | High | Medium | Strict P0-P4 phases, no jumping ahead |
| vLLM complexity | Medium | Medium | Use existing examples, don't rebuild from scratch |
| Memory design flaws | Medium | High | Design simple first, scale as needed |
| Parallel execution conflicts | High | Medium | Test heavily, add guards/rate limits |

---

## Appendix: Quick Wins

During implementation, these provide immediate value while building:

1. **Documentation-first**: Write docs, examples as code goes in
2. **Release candidate P0 immediately**: Test, iterate
3. **Build one agent fully**: Show complete workflow
4. **One real use case**: Find a problem you actually need solved

### Sample "First" Tasks

```bash
# 1. Test P0: vLLM + basic query
node scripts/test_vllm.js "What is RAG?"

# 2. Test P1: Simple research
node scripts/test_researcher.js "Research transformer attention"

# 3. Test P2: Multi-agent
node scripts/test_planner.js "Compare RAG vs REAG"
```

---

## License & Attribution

This expansion plan was created by Deep Agent Code (dcode) using Qwen3.5-9B (4-bit AWQ quantization, served locally via vLLM). No enterprise subscriptions or paid tools were used in the design process.

---

## Contact

For questions or contributions to this expansion plan, see the GitHub issues.
