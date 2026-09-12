# my-rxer Expansion Plan

> **Created by Deep Agent Code (dcode)**  
> **Model**: Qwen3.5-9B (4-bit AWQ via vLLM)  
> **Date**: 2025

---

## Executive Summary

This document outlines the roadmap for evolving `/home/dev/workspace/lnd/aiops/apps/my-rxer` from a foundational agent framework into a **full-pledged multi-agent system** capable of autonomous research, knowledge synthesis, and complex problem-solving.

### Current State Assessment

- **Maturity Level**: ~20-25% toward full-featured multi-agent system
- **Architecture**: Hybrid modular 3-tier hierarchy designed
- **Code Status**: Core framework complete (71/71 tests passing), skill prototypes pending
- **Components**: Task queue, workers, registry, logger, memory manager all functional
- **Tests**: 100% pass rate achieved on core components via TDD approach

### Target State

- **Maturity Level**: 95%+ (production-ready multi-agent system)
- **Architecture**: Hybrid modular with 3-tier hierarchy
- **Capabilities**: Multiple autonomous agents collaborating on complex tasks
- **Use Cases**: 7+ distinct research and analysis workflows

---

## Architecture: Hybrid Modular Design

### The 3-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       TIER 3: AGENTS                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐    │
│  │   Planner  │  │   Researcher │  │    Writer   │  │Critic │    │
│  └────────────┘  └────────────┘  └────────────┘  └────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Scheduler (Orchestrator)                │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                       TIER 2: SKILLS                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐    │
│  │   Search   │  │ Extraction │  │  Synthesis  │  │ Critique │  │
│  │            │  │            │  │             │  │         │    │
│  │  Analysis  │  │  Querying  │  │ Knowledge  │  │Reasoning│  │
│  │            │  │   Tools    │  │ Assembly   │  │         │    │
│  └────────────┘  └────────────┘  └────────────┘  └────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                       TIER 1: TOOLS                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐    │
│  │   LLM      │  │   Web      │  │   File     │  │Memory  │    │
│  │ Client     │  │  API Client│  │   Access   │  │  Mgr     │  │
│  │ (vLLM/BGE) │  │            │  │            │  │         │    │
│  └────────────┘  └────────────┘  └────────────┘  └────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 3: Advanced Agents

**Tier 3** includes multiple autonomous agents that collaborate on complex tasks:

1. **Planner Agent**: Breaks down complex research topics into subtasks
2. **Researcher Agent**: Executes the subtasks using appropriate skills
3. **Writer Agent**: Formats and structures research outputs
4. **Critic Agent**: Evaluates work and suggests improvements
5. **Scheduler Agent**: Coordinates parallel execution and task distribution

---

## Use Case Categories

### Use Case #1: Autonomous AI Research

**Description**: Given a research topic, autonomously search across multiple sources, synthesize findings, and deliver a comprehensive research report.

**Example**:
```
User: "Research the latest developments in RAG (Retrieval-Augmented Generation)"

Agent:
  1. Searches arXiv, Hugging Face, Medium, ar.us, AIResearch.com
  2. Extracts and classifies relevant papers
  3. Synthesizes findings into a structured report
  4. Outputs research summary with citations
```

**Acceptance Criteria**:
- [ ] Can search 4+ different sources
- [ ] Can synthesize information across sources
- [ ] Produces structured, well-formatted output
- [ ] Includes proper citations and sources
- [ ] Takes 5-10 minutes for typical research queries

**Complexity**: High  
**Effort**: P1 (Core) - 40-60 hours

---

### Use Case #2: Cross-Capabilities Analysis

**Description**: Analyze and compare multiple research methodologies or technical approaches on the same topic.

**Example**:
```
User: "Compare different approaches to image captioning

Agent:
  1. Identifies 3+ distinct methodologies
  2. Searches for academic papers and benchmarks
  3. Structures comparison table with pros/cons
  4. Outputs analysis with recommendations
```

**Acceptance Criteria**:
- [ ] Can identify multiple distinct approaches
- [ ] Provides structured comparison (table or matrix)
- [ ] Includes technical implementation details
- [ ] Lists trade-offs, strengths, and limitations
- [ ] Generates implementation recommendations

**Complexity**: Medium-High  
**Effort**: P1 - 40-80 hours

---

### Use Case #3: Interactive Learning Agent

**Description**: Provide explanations of complex AI concepts with multiple approaches and depth levels.

**Example**:
```
User: "Explain transformers to me"

Agent:
  1. Requests user's background/proficiency level
  2. Reads and analyzes relevant educational material
  3. Selects appropriate complexity level
  4. Tries multiple explanation strategies
  5. Provides intuitive examples and analogies
  6. Offers follow-up questions for deeper understanding
```

**Acceptance Criteria**:
- [ ] Can adapt complexity based on user needs
- [ ] Provides multiple explanation strategies
- [ ] Includes code examples where appropriate
- [ ] Offers intuitive examples/analogies
- [ ] Generates follow-up questions for self-assessment

**Complexity**: Medium  
**Effort**: P2 - 50-100 hours

---

### Use Case #4: Knowledge Base Curation

**Description**: Ingest papers, research articles, or documentation and create a structured knowledge graph.

**Example**:
```
User: "Build a knowledge graph from 100+ papers on LLMs

Agent:
  1. Downloads or indexes 100+ papers
  2. Extracts key entities, concepts, relationships
  3. Generates structured knowledge graph (GND format)
  4. Stores in graph database or connected index
  5. Provides query interface
```

**Acceptance Criteria**:
- [ ] Can ingest 100+ documents at batch speed
- [ ] Extracts structured entities and relationships
- [ ] Creates connectable knowledge graph
- [ ] Allows querying relationships
- [ ] Supports export formats (GND, JSON, graphviz)

**Complexity**: High  
**Effort**: P2 - 60-120 hours

---

### Use Case #5: Competitive Monitoring

**Description**: Continuously scan for breakthrough research, alert on new developments, and track field progress.

**Example**:
```
User: "Track the latest diffusion model breakthroughs

Agent:
  1. Monitors arXiv, GitHub, Medium daily
  2. Classifies new papers on-topic/related/off-topic
  3. Extracts key advances and impact
  4. Alerts on breakthrough-level findings
  5. Generates weekly summary report
```

**Acceptance Criteria**:
- [ ] Can run automated daily scans
- [ ] Classifies papers by relevance and impact
- [ ] Alerts on high-impact findings only
- [ ] Generates structured weekly summaries
- [ ] Maintains running field state/log

**Complexity**: Medium  
**Effort**: P2 - 40-60 hours

---

### Use Case #6: Multi-Task Batch Processing

**Description**: Execute multiple research tasks in parallel while managing resources and dependencies.

**Example**:
```
User: "Research 3 AI topics in parallel: RAG, agent planning, and long-context windows

Agent:
  1. Parses the 3 topics into subtasks
  2. Assigns agents to each topic parallelly
  3. Monitors progress across tasks
  4. Rebalances load based on completion
  5. Aggregates results into final report
```

**Acceptance Criteria**:
- [ ] Can launch 3+ parallel research tasks
- [ ] Manages resource allocation across agents
- [ ] Blocks on task dependencies when needed
- [ ] Rebalances load dynamically
- [ ] Produces aggregated final output

**Complexity**: Medium-High  
**Effort**: P2-P3 - 60-80 hours

---

### Use Case #7: Self-Correcting System

**Description**: Autonomous research that includes self-critique and revision cycles for accuracy and quality control.

**Example**:
```
User: "Research agentic AI planning methods

Agent:
  1. Plans comprehensive research strategy
  2. Executes multi-step research workflow
  3. Produces initial draft
  4. Runs work through Critic agent
  5. Critic suggests specific corrections
  6. System iterates improvements
  7. Final verified output ready for delivery
```

**Acceptance Criteria**:
- [ ] Can generate initial research draft
- [ ] Executes self-critique on the work
- [ ] Identifies specific errors/weaknesses
- [ ] Iterates on corrections multiple times
- [ ] Validates improved version against critique
- [ ] Produces higher-quality final output

**Complexity**: High  
**Effort**: P3 - 60-120 hours

---

## Implementation Phased Roadmap

### Phase P0: Core Foundation (~50-70 hours)

**Goal**: Establish the infrastructure that enables all future agents with containerized deployment support.

**Skills to Build**:
- [ ] Worker class with registry system (Python, asyncio)
- [ ] Tool abstraction (LLM, web, file, memory)
- [ ] Task queue and execution model
- [ ] Basic logging and observability
- [ ] Container orchestration integration

**Tools to Build**:
- [ ] LLM client wrapper (vLLM + BGE via Python)
- [ ] Web scraper/API client (aiohttp)
- [ ] File system access
- [ ] Basic memory manager (in-process + Redis/SQLite)

**Non-Functional Requirements**:

1. **Containerization (MCP Tool Compliance)**:
   - Docker Compose setup for isolated environment
   - vLLM server container for LLM inference
   - my-rxer application container
   - Persistent volume mounts for model weights
   - Health check endpoints

2. **Performance**:
   - Async I/O for all I/O-bound operations
   - Connection pooling for HTTP requests
   - Worker concurrency control
   - Latency < 5s for typical queries

3. **Reliability**:
   - Graceful shutdown on SIGTERM
   - Circuit breakers for external service calls
   - Retry logic for transient failures
   - Automatic reconnection to vLLM backend

4. **Security**:
   - Environment variable configuration (no hardcoded secrets)
   - Input validation for all tool calls
   - Rate limiting for external APIs
   - Sandboxed worker execution

5. **Observability**:
   - Structured JSON logging
   - Request ID tracking across services
   - Basic metrics (latency, throughput, errors)
   - Docker container health metrics

**Docker Requirements**:
- Docker 20.10+
- docker-compose 2.0+
- vLLM backend container
- Redis for optional persistent memory
- Python 3.10+ virtual environment in container

**Acceptance**: Infrastructure enables simple tool-chaining workflows with isolated, containerized deployment

**Estimate**: 4-6 days of sustained work (increased from 3-5 due to containerization)

---

### Phase P1: Core Agents (~40-80 hours)

**Goal**: Implement the first functional agent capable of autonomous research.

**Agent to Build**:
- [ ] Research Agent (plans + executes research tasks)
- [ ] Writer Agent (formats research outputs)

**Skills to Build**:
- [ ] Search skill (web, academic sources)
- [ ] Extraction skill (information parsing)
- [ ] Synthesis skill (combining information)
- [ ] Analysis skill (summarizing findings)
- [ ] Citation skill (proper attribution)

**Acceptance**: Can complete full research flow from prompt to output

**Estimate**: 3-5 days of sustained work

---

### Phase P2: Multi-Agent Communication (~50-100 hours)

**Goal**: Add 3-4 more agents and establish communication protocols.

**Agents to Build**:
- [ ] Planner Agent (task breakdown)
- [ ] Scheduler Agent (parallel task coordination)
- [ ] Critic Agent (work evaluation and suggestions)

**Communication Layer**:
- [ ] Message bus / task queue
- [ ] Inter-agent protocols
- [ ] Shared state management

**Acceptance**: Multiple agents can collaborate on complex tasks

**Estimate**: 5-7 days of sustained work

---

### Phase P3: Advanced Patterns (~60-120 hours)

**Goal**: Implement metacognition and self-correction capabilities.

**Features to Build**:
- [ ] Self-reflection mechanism
- [ ] Critic agent reviews and revisions
- [ ] Running knowledge graph / field log
- [ ] Analytical Network Framework (ANN) patterns:
  - [ ] Consensus with multiple agents
  - [ ] Task decomposition with skill scaffolding
  - [ ] Agent rounds with backswing
  - [ ] Shared archives with document linking

**Acceptance**: Can self-improve work through critique cycles

**Estimate**: 4-7 days of sustained work

---

### Phase P4: Production Features (~60-80 hours)

**Goal**: Make the system production-ready with robust monitoring and configuration.

**Features to Build**:
- [ ] Full configuration file with all options
- [ ] Persistence layer (vector/graph DB integration)
- [ ] Multi-step task orchestration
- [ ] Error recovery and retry mechanisms
- [ ] Performance monitoring and metrics
- [ ] Web UI / API for interaction

**Acceptance**: System is usable in non-interactive contexts

**Estimate**: 4-6 days of sustained work

---

## Skills Organization Strategy

### Current Skills

| File | Description | Status |
|------|-------------|--------|
| `search-skill.md` | Web search and source finding | Prototype |
| `knowledge-skill.md` | Extract and store knowledge | Prototype |

### New Skills to Add

#### Core Skills (P0-P1)

| Skill | Description | Priority |
|-------|-------------|----------|
| **Search** | Multi-source web and academic search | P0 |
| **Extraction** | Parse documents and extract structured data | P0 |
| **Synthesis** | Combine multiple sources into cohesive output | P1 |
| **Analysis** | Summarize and analyze synthesized content | P1 |
| **Summarization** | Create various output formats (brief, detailed, Q&A) | P1 |

#### Advanced Skills (P2-P3)

| Skill | Description | Priority |
|-------|-------------|----------|
| **Planning** | Break complex tasks into actionable subtasks | P2 |
| **Reasoning** | Multi-step logical deduction and inference | P3 |
| **Critique** | Evaluate work quality and suggest improvements | P2 |
| **Citation** | Generate proper citations and attributions | P1 |
| **Formatting** | Multiple output formats (Markdown, tables, code) | P1 |

---

## Research Methodologies to Implement

### ANN (Analytical Network Framework) Style

1. **Task Decomposition**
   - Full workbreakdown structure
   - Skill scaffolding for each node
   - Agent assignment based on subtask

2. **Consensus**
   - Multiple agents evaluate same task
   - Aggregate consensus via democratic process
   - Disagreement triggers further analysis

3. **Working Libraries**
   - Keep running library of information
   - Link to different documents recursively
   - Limited to fixed number of originals
   - Handles factual and combinatorial linkages

4. **Chunked Processing**
   - Split corpus by unknown type: span
   - Feed to larger libraries custom-tuned
   - Pass specific library chunks directly

5. **Message Boards**
   - Contextual notes pass back and forth
   - Keep notes short enough for quick scanning
   - Notes remain meaningful across longer tasks

6. **Archive**
   - Document corpus + answers + examples
   - Search and see-in-context links
   - Provides unified context for thinking

### Additional Methodologies

- **Meta-Thinking**: Reverse-engineer and improve own processes
- **Hypothetical Thinking**: Consistent hypotheses to modify
- **Evaluating Work**: Critique and analyze own outputs
- **Skill Management**: List all skills with descriptions
- **Resource Allocation**: Distribute computational resources efficiently

---

## Timeline and Effort Estimates

### Summary Table

| Phase | Major Feature | Effort | Cumulative |
|-------|---------------|--------|------------|
| P0 | Core Foundation | 40-60h | 40-60h |
| P1 | Core Agents | 80-120h | 120-180h |
| P2 | Multi-Agent | 100-140h | 220-320h |
| P3 | Advanced Patterns | 120-180h | 340-500h |
| P4 | Production | 100-140h | 440-640h |

### Total: 150-250 hours hands-on time

### Weekly Pace Options

| Pace | Hours/Week | Duration | Completion |
|------|-----------|----------|------------|
| Intensive | 40h | 6-10 weeks | Full system P0-P4 |
| Steady | 20h | 12-20 weeks | Full system P0-P4 |
| Sporadic | 10h | 25-50+ weeks | Full system P0-P4 |
| Minimal | 5h | 30-50+ weeks | Partial system P0-P3 |

---

## Non-Functional Requirements

### 1. **Containerization (MCP Tool Support)** ⭐

**Strategy**: Triple-tier containerized architecture

```yaml
# docker-compose.yml
version: '3.8'

services:
  # LLM inference layer
  vllm-backend:
    build: ./vllm-container
    ports:
      - "8000:8000"
    volumes:
      - ./models:/models
      - ./config:/config
    environment:
      - VLLM_PORT=8000
    restart: unless-stopped
    health_check:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Main application
  my-rxer-app:
    build: ./
    depends_on: [vllm-backend]
    ports:
      - "8080:8000"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    environment:
      - VLLM_URL=http://vllm-backend:8000
      - REDIS_HOST=redis
    restart: unless-stopped

  # Memory layer (optional)
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    health_check:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

networks:
  default:
    driver: bridge
```

### 2. **Language & Dependencies**

**Current**: Node.js/npm with Python runtime available
**Recommendation**: Define `package.json` with tool dependencies
- Use `deepagent` npm package core
- Add `langchain` or `langgraph.js` for production capabilities
- Include `longpotat` for structured output
- Add `plan` package for task decompostion

### 2. **Memory & Persistence**

**Current**: In-process only
**Recommendation**: Add persistence layers:
- **Vector DB**: For semantic search and retrieval
- **Graph DB**: For knowledge graphs and relationships
- **Local storage**: For quick caching and temp state
- **Redis/SQLite**: For structured data and queues

### 3. **LLM Integration**

**Current**: vLLM locally hosted with Qwen3.5-9B
**Recommendation**: Plan for flexibility:
- [ ] vLLM client wrapper (local inference)
- [ ] OpenAI-compatible bridge (remote API)
- [ ] HuggingFace client wrapper (open weights)
- [ ] Fallback routing for reliability

### 4. **Communication & Orchestration**

**Current**: None
**Recommendation**: Design a robust communication layer:
- [ ] Message bus for inter-agent messaging
- [ ] Lightweight task queue scheduler
- [ ] Shared state management
- [ ] Error handling and retry mechanisms

### 5. **Evaluation & Testing**

**Current**: None
**Recommendation**: Establish quality gates:
- [ ] Unit tests for core worker class
- [ ] Integration tests for agent-tool interactions
- [ ] Functional tests for complete workflows
- [ ] Performance benchmarks
- [ ] User acceptance criteria automation

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| vLLM reliability | High | Implement fallback systems and caching |
| Skill complexity | Medium | Prototype iterative, validate early |
| Multi-agent comms | High | Use established patterns from research |
| State persistence | Medium | Start simple, scale as needed |
| Documentation lag | Medium | Document as you build |

### Implementation Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | High | Stick to prioritized roadmap |
| Feature overload | Medium | Build only what's necessary |
| Team bandwidth | High | Phased approach with clear milestones |
| Technical debt | Medium | High code quality checks |
| Complexity spiral | High | Keep architecture modular |

---

## Success Metrics

### Quantitative Metrics

- [ ] Can complete autonomous research task end-to-end
- [ ] Supports 3+ concurrent autonomous agents
- [ ] Supports 5+ different skills
- [ ] Handles 100+ document memory persistence
- [ ] Executes multi-step tasks in parallel
- [ ] Self-correction improves output quality

### Qualitative Metrics

- [ ] Outputs are accurate and useful
- [ ] System feels "intelligent" and responsive
- [ ] Can handle unexpected queries gracefully
- [ ] Documentation is comprehensive
- [ ] Code is maintainable and extensible
- [ ] User perceives value in outputs

---

## Conclusion

This expansion plan transforms my-rxer from a foundational framework into a complete multi-agent research system. The hybrid modular architecture balances complexity with maintainability, starting with core foundations and iterating toward advanced patterns.

**Key Decision Points**:
1. **Go Full-Pledged**: Yes - the value is in multi-agent collaboration
2. **Phased Approach**: Yes - build iteratively P0-P4
3. **Test Each Phase**: Yes - each milestone should be functional
4. **Documentation Along the Way**: Yes - capture learnings as you go

The ~200 hours required for phases P0-P4 represents a significant commitment but yields a fully functional autonomous research system with multiple use cases.

---

> **Generated by Deep Agent Code (dcode)**  
> **Model**: Qwen3.5-9B (4-bit AWQ)  
> **Service**: Locally hosted vLLM
