# my-rxer: AI Research Agentic Framework

## High-Level Design (HLD)

### 1. Overview

**Purpose**: my-rxer is an autonomous agent-based system designed for AI research, discovery, and knowledge synthesis. It enables programmable AI research workflows through a modular, extensible architecture.

**Vision**: Create a full-featured multi-agent system that can autonomously conduct research, synthesize knowledge, and generate insights across diverse AI topics.

**Current Maturity**: ~25% (Alpha+ phase) - Core infrastructure complete, skill prototypes pending

**Target Maturity**: 95%+ (Production-ready multi-agent system)

**Model Stack**:
- **LLM**: Qwen3.5-9B (4-bit AWQ)
- **Inference**: Local vLLM server
- **Hosting**: Zero-cost open weights

---

### 2. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                           my-rxer System                                │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    TIER 3: AGENTS LAYER                          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐   │  │
│  │  │  Planner   │  │ Researcher │  │   Writer   │  │Critic  │   │  │
│  │  └──────┬─────┘  └────┬───────┘  └────┬───────┘  └────┬───┘   │  │
│  │         │             │               │               │       │  │
│  │  ┌──────▼─────────────────────────────────────────────▼──────┐  │  │
│  │  │              Scheduler/Orchestrator                        │  │  │
│  │  └───────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       TIER 2: SKILLS                             │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐   │  │
│  │  │   Search   │  │  Analysis  │  │ Synthesis  │  │ Reasoning│  │  │
│  │  │    Engine  │  │             │  │            │  │         │   │  │
│  │  │  Knowledge │  │ Query Tools │  │ Assembly   │  │Tools    │   │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────┘   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       TIER 1: TOOLS                               │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐   │  │
│  │  │   LLM      │  │   WebClient│  │   File     │  │ Memory │   │  │
│  │  │  Client    │  │   (HTTP)   │  │   System   │  │Manager │   │  │
│  │  │ (vLLM/BGE) │  │aiohttp     │  │  Access    │  │  (Redis)│   │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────┘   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      INFRASTRUCTURE LAYER                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐       │  │
│  │  │  vLLM    │  │  Docker  │  │  Redis   │  │ MCP Server │       │  │
│  │  │  Server  │  │ Compose  │  │  (Memory │  │ HTTP A      │       │  │
│  │  │          │  │  Orchest  │  │  Store)  │  │  Interface  │       │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────┘       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Component Boundaries & Interfaces

#### 3.1 Agents Layer (Tier 3)

| Component | Responsibility | Communication |
|-----------|---------------|---------------|
| **Planner** | Breaks complex tasks into subtasks, defines research strategy | Receives task from Scheduler; returns task list |
| **Researcher** | Executes search, extraction, and analysis operations | Calls Skills layer tools; returns findings |
| **Writer** | Formats content, generates structured outputs | Receives findings; produces markdown/text |
| **Critic** | Evaluates outputs, suggests improvements | Receives written content; provides critique |
| **Scheduler** | Coordinates parallel execution, distributes work | Orchestrates between agents; gets feedback |

#### 3.2 Tools Layer (Tier 1)

| Component | Responsibility | Output |
|-----------|---------------|--------|
| **LLMClient** | Interface to vLLM/BGE models | Text completions, structured responses |
| **WebClient** | HTTP requests, web scraping, API calls | HTTP responses, scraped content |
| **FileSystem** | Read/write files, local storage | File paths, content, metadata |
| **MemoryManager** | Persistent memory store using Redis | Key-value pairs, memory graphs |

---

### 4. Data Flow

#### 4.1 High-Level Request Flow

```
User Request
    ↓
Scheduler (receives task)
    ↓
Planner → breaks into subtasks
    ↓
Multiple Researcher workers (parallel)
    ↓
Skills layer (Search, Analysis, Synthesis)
    ↓
Results → Writer → formatted output
    ↓
Critic → suggestions
    ↓
Iterate until validation → Final output to User
```

#### 4.2 Task Queue & Worker Lifecycle

```
User submits task
    ↓
Task queued with priority (high/medium/low)
    ↓
WorkerRegistry selects available worker
    ↓
Worker claims task from queue
    ↓
Worker executes using appropriate Skills
    ↓
Task completes → TaskResult stored
    ↓
Callback notifies calling code
```

---

### 5. Non-Functional Requirements

### 5.1 Performance
- **Task Processing**: 5-10ms per operation for core queue operations
- **Worker Response**: <100ms for task assignment (typical)
- **LLM Latency**: Dependent on vLLM server (measured)
- **Memory Access**: <10ms typical Redis latency

### 5.2 Scalability
- **Workers**: Horizontally scalable via Docker compose
- **Memory**: Sharded Redis deployment for high concurrency
- **LLM**: GPU resources via vLLM, can scale with model replicas
- **Message Queue**: Priority-based task distribution

### 5.3 Reliability
- **Task Persistence**: Critical tasks stored in durable storage
- **Retry Logic**: Exponential backoff for transient failures
- **Failover**: Worker pool auto-scaling on worker loss
- **Monitoring**: Structured JSON logging with health checks

### 5.4 Security
- **Memory Isolation**: Redis for distributed state
- **Model Isolation**: vLLM container separation
- **API Security**: MCP server access control (to be defined)
- **Data Privacy**: Local-only deployment (no external leaks)

---

## Low-Level Design (LLD)

### 6. Core Components - Detailed Design

#### 6.1 TaskQueue Manager

**Responsibilities:**
- Manage priority task queue
- Handle task assignment and completion
- Support callbacks on completion
- Provide timeout and retry mechanisms

**Class Structure:**
```python
class TaskQueueManager:
    '''Priority-based async task queue with worker coordination'''
    
    async def submit(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        priority: Priority = Priority.MEDIUM,
        timeout: Optional[int] = None,
        callback: Optional[Callable] = None
    ) -> TaskResult:
        pass
    
    async def _process_tasks(self) -> None:
        '''Main worker loop for processing queued tasks'''
        pass
    
    async def assign_task(
        self,
        task_id: str,
        worker_id: str
    ) -> bool:
        pass
```

**State Machine:**
```
QUEUED -> ASSIGNED -> IN_PROGRESS -> COMPLETED/FAILED/TIMEOUT
```

**Key Invariants:**
- Tasks with higher priority are processed first
- Each task assigned to at most one worker
- Timeout after N seconds triggers task reassignment
- Callbacks invoked after successful completion

---

#### 6.2 Worker Base Class

**Responsibilities:**
- Abstract base for all worker types
- Worker lifecycle management (start/stop)
- Task execution coordination
- Result aggregation

**Key Methods:**
```python
class Worker(ABC):
    '''Abstract worker implementation'''
    
    def __init__(
        self,
        worker_id: str,
        worker_type: WorkerType,
        manager_ref: Optional[WorkerManager] = None
    ):
        pass
    
    async def start(self) -> bool:
        '''Start the worker and begin task processing'''
        pass
    
    async def stop(self, graceful: bool = True) -> None:
        '''Stop worker, optionally with graceful shutdown'''
        pass
    
    async def run_tasks(self) -> WorkerResult:
        '''Core task loop for processing'''
        pass
    
    async def execute_task(
        self,
        task: Task
    ) -> TaskResult:
        '''Execute a single task with retry logic'''
        pass
    
    def register_callback(
        self,
        callback: Callable[[TaskResult], Any]
    ):
        '''Register callback for completion notification'''
        pass


# Specialized Workers
class LLMWorker(Worker):
    '''Worker for LLM-based tasks'''
    pass


class WebWorker(Worker):
    '''Worker for web scraping/API calls'''
    pass


class MemoryWorker(Worker):
    '''Worker for memory management tasks'''
    pass
```

---

#### 6.3 WorkerRegistry

**Responsibilities:**
- Manage worker pool lifecycle
- Select appropriate worker for tasks
- Handle worker registration/unregistration
- Monitor worker health

**Class Structure:**
```python
class WorkerRegistry:
    '''Coordinates worker pool and task distribution'''
    
    def __init__(
        self,
        config: WorkerConfig,
        worker_factory: Callable[[], Worker]
    ):
        pass
    
    async def spawn_worker(
        self,
        worker_type: WorkerType,
        worker_id: str = None
    ) -> Worker:
        '''Create and register new worker'''
        pass
    
    async def stop_worker(
        self,
        worker_id: str
    ) -> bool:
        '''Stop a specific worker'''
        pass
    
    async def stop_all_workers(self, graceful: bool = True) -> None:
        '''Stop all workers in the pool'''
        pass
    
    async def select_worker(
        self,
        task_requirements: TaskRequirements
    ) -> Optional[Worker]:
        '''Select best worker for given task '''
        pass
```

---

#### 6.4 Memory Manager (Redis-based)

**Responsibilities:**
- Distributed key-value storage
- Memory graph support
- Persistent state management
- Multi-node support via Redis

**Interfaces:**
```python
class MemoryManager:
    '''Redis-based distributed memory store'''
    
    async def save(
        self,
        key: str,
        data: Any,
        ttl: Optional[int] = None
    ) -> bool:
        '''Save data with optional TTL'''
        pass
    
    async def get(
        self,
        key: str
    ) -> Optional[Any]:
        '''Retrieve data by key'''
        pass
    
    async def graph_store(
        self,
        graph_name: str,
        nodes: List[Dict],
        edges: List[Dict]
    ) -> bool:
        '''Store knowledge graph'''
        pass
    
    async def graph_query(
        self,
        graph_name: str,
        query: str
    ) -> Dict:
        '''Execute graph query'''
        pass
    
    async def close(self) -> None:
        '''Close connections'''
        pass
```

---

#### 6.5 Logger (Structured)

**Responsibilities:**
- JSON-formatted structured logging
- Log level filtering
- Timestamped entries with correlation IDs
- Multiple output formats (JSON, file, console)

```python
class Logger:
    '''Structured JSON logger for my-rxer'''
    
    def __init__(
        self,
        name: str,
        log_file: str,
        level: str = "INFO"
    ):
        pass
    
    def _log(
        self,
        level: str,
        message: str,
        extra: Dict = None
    ) -> None:
        pass
    
    def debug(self, message: str, **extra):
        pass
    
    def info(self, message: str, **extra):
        pass
    
    def warning(self, message: str, **extra):
        pass
    
    def error(self, message: str, **extra):
        pass
    
    def critical(self, message: str, **extra):
        pass
```

**Structured Log Example:**
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "correlation_id": "abc-123",
  "logger": "my-rxer.Worker",
  "message": "Task completed successfully",
  "task_id": "task-001",
  "duration_ms": 2341
}
```

---

#### 6.6 LLMClient (Tool Abstraction)

**Responsibilities:**
- Interface to local vLLM model
- Prompt formatting and response parsing
- Streaming support
- Context management

```python
class LLMClient:
    '''Interface to local LLM via vLLM'''
    
    def __init__(
        self,
        endpoint: str = "http://localhost:8000",
        context_length: int = 4096
    ):
        pass
    
    async def generate(
        self,
        prompt: str,
        system: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        pass
    
    async def generate_structured(
        self,
        prompt: str,
        schema: Dict
    ) -> Any:
        '''Generate JSON-structured output'''
        pass
    
    async def stream(
        self,
        prompt: str
    -> AsyncGenerator[str, None]
    ):
        '''Stream token-by-token generation'''
        pass
```

---

#### 6.7 WebClient (Tool Abstraction)

**Responsibilities:**
- HTTP requests (sync/async)
- Web scraping support
- API integration
- Request rate limiting
- Error handling with retries

```python
class WebClient:
    '''Async HTTP client and web scraper'''
    
    def __init__(
        self,
        timeout: int = 30,
        retries: int = 3
    ):
        pass
    
    async def get(
        self,
        url: str,
        params: Dict = None,
        headers: Dict = None
    ) -> Response:
        pass
    
    async def post(
        self,
        url: str,
        data: Dict = None,
        json: Dict = None
    ) -> Response:
        pass
    
    async def fetch(
        self,
        url: str
    ) -> str:
        '''Fetch page content as string'''
        pass
    
    async def scrape(
        self,
        url: str,
        extraction_schema: Dict = None
    ) -> Dict:
        '''Scrape and extract structured data'''
        pass
```

---

#### 6.8 ToolAbstractionLayer

**Responsibilities:**
- Encapsulate all tool interactions
- Dependency injection for tool instances
- Unified interface for all worker types
- Tool health monitoring

```python
class ToolAbstractionLayer:
    '''Unified interface for all infrastructure tools'''
    
    def __init__(
        self,
        llm_client: LLMClient,
        web_client: WebClient,
        file_client: FileSystemClient,
        memory_manager: MemoryManager,
        logger: Logger
    ):
        self._llm = llm_client
        self._web = web_client
        self._file = file_client
        self._memory = memory_manager
        self._logger = logger
    
    async def llm_generate(self, prompt: str, ...) -> str:
        pass
    
    async def web_fetch(self, url: str, ...) -> str:
        pass
    
    async def file_read(self, path: str) -> str:
        pass
    
    async def memory_store(self, key: str, data: Any) -> bool:
        pass
    
    async def memory_retrieve(self, key: str) -> Optional[Any]:
        pass
```

---

### 7. Use Case Implementations

#### 7.1 Use Case #1: Autonomous AI Research

**Component Design:**

```python
class AutonomousResearchAgent:
    '''End-to-end autonomous research agent'''
    
    def __init__(
        self,
        registry: WorkerRegistry,
        tool_layer: ToolAbstractionLayer
    ):
        self._registry = registry
        self._tools = tool_layer
        self._search_methods = [
            SmithOMatic(),
            DuckDuckGo(),
            ScholarSearch()
        ]
    
    async def research(self, topic: str) -> ResearchReport:
        '''Execute full research workflow'''
        
        # Phase 1: Information gathering
        search_plan = await self._planner.plan_search(topic)
        
        search_results = await asyncio.gather(
            *[self._searcher.search(topic, method) 
              for searcher, method in zip(self._searchers, search_plan)]
        )
        
        # Phase 2: Extraction and synthesis
        analyzed_content = await self._analyzer.analyze(search_results)
        synthesized_report = await self._synthesizer.write(analyzed_content)
        
        # Phase 3: Critique and iteration
        critique = await self._critic.evaluate(synthesized_report)
        
        if critique.summary:
            improved_report = await self._synthesizer.iterate(
                synthesized_report, critique.suggestions
            )
        else:
            improved_report = synthesized_report
        
        return improved_report
```

**Data Flow:**
```
User: "Research RAG techniques"
    ↓
AutonomousResearchAgent
    ↓
Planner → defines search strategy
    ↓
WebWorkers (parallel) → search multiple sources
    ↓
ExtractionWorker → parse and structure
    ↓
SynthesisWorker → aggregate findings
    ↓
CriticWorker → evaluate report quality
    ↓
WriterWorker → polished final report
    ↓
User receives comprehensive research summary
```

**Performance Targets:**
- Search phase: 2-3 minutes
- Analysis phase: 1-2 minutes  
- Synthesis phase: 1 minute
- Total: 5-6 minutes for typical 5-page report

---

#### 7.2 Use Case #2: Cross-Capabilities Analysis

**Component Design:**

```python
class ComparativeAnalysisAgent:
    '''Compares multiple approaches to a problem'''
    
    def __init__(
        self,
        registry: WorkerRegistry,
        tool_layer: ToolAbstractionLayer
    ):
        self._registry = registry
        self._tools = tool_layer
    
    async def analyze_comparison(
        self,
        topic: str,
        approaches: List[str],
        depth_level: str = "comprehensive"
    ) -> ComparativeAnalysisReport:
        pass
```

**Output Structure:**
```python
class ComparativeAnalysisReport:
    '''Structured comparison output'''
    
    @dataclass
    class ComparisonEntry:
        approach: str
        description: str
        pros: List[str]
        cons: List[str]
        complexity: str
        performance: str
        use_cases: List[str]
    
    theory: str
    comparisons: List[ComparisonEntry]
    summary: str
    recommendation: str
    implementation_notes: str
```

---

### 8. API Specifications

#### 8.1 MCP Server Interfaces

```typescript
interface MCPTool {
    name: string;
    description: string;
    parameters: {
        type: "object";
        properties: {
            [key: string]: {
                type: "string" | "number" | "boolean" | "object" | "array";
                description: string;
                required?: boolean;
            }
        };
        required?: string[];
    };
    returnType: "string" | "object" | "array";
}

// 7 MCP Tools
interface MCPToolsAPI {
    tools: {
        llm_generate: (params: { prompt: string; options?: LLMOptions }) => Promise<{ output: string }>;
        web_search: (params: { query: string; limit?: number }) => Promise<{ results: SearchResult[] }>;
        web_scrape: (params: { url: string }) => Promise<{ content: string; metadata: URLMetadata }>;
        file_read: (params: { path: string }) => Promise<{ content: string }>;
        file_write: (params: { path: string; content: string }) => Promise<{ success: boolean }>;
        memory_store: (params: { key: string; value: any }) => Promise<{ success: boolean }>;
        memory_retrieve: (params: { key: string }) => Promise<{ value?: any; found: boolean }>;
    };
}
```

#### 8.2 Web Agent Interfaces (for my-rxer/webagents)

```python
class WebSpider(ABC):
    '''Abstract base for web spiders'''
    
    @abstractmethod
    async def scrape(self, url: str) -> ScrapedData:
        pass
    
    @abstractmethod
    async def classify(self, content: str) -> str:
        '''Classify content type'''
        pass
    
    @property
    @abstractmethod
    def priority(self) -> Priority:
        '''Spider task priority'''
        pass
```

---

### 9. Database/Redis Schemas

#### 9.1 Memory Store

```redis
# Key-value pairs (general storage)
my-rxer:{cache} → <value>

# Task queue
task_queue:active:{task_id} → {task_data}
task_queue:completed:{task_id} → {result_data}

# Worker state
worker:{id}:status → "ACTIVE" | "IDLE" | "BUSY"
worker:{id}:tasks_processed → <count>

# Graph structures (knowledge graph)
knowledge_graph:{topic} → {nodes, edges}
  nodes: [{id, type, attributes}]
  edges: [{source, target, type, attributes}]
```

#### 9.2 Knowledge Graph Schema

```python
class KnowledgeNode:
    '''Node in a knowledge graph'''
    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        attributes: Dict[str, Any]
    ):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.attributes = attributes
    
    # Relationships
    def add_relaton
