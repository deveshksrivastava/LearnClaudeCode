export interface Project {
  title: string;
  slug: string;
  category: string;
  color: string;
  iconBg: string;
  iconColor: string;
  borderHover: string;
  shortDesc: string;
  fullDesc: string;
  status: string;
  statusBg: string;
  statusTextColor: string;
  progress: number;
  checklist: string[];
  techStack: string[];
  team: { name: string; role: string; avatar: string }[];
  timeline: { date: string; event: string }[];
  links: { label: string; url: string }[];
}

export const PROJECTS: Project[] = [
  {
    title: 'RAG Pipeline',
    slug: 'rag-pipeline',
    category: 'Core AI Engineering',
    color: '#6366f1',
    iconBg: 'bg-indigo-100',
    iconColor: 'text-indigo-600',
    borderHover: 'hover:border-indigo-300',
    shortDesc: 'Build a production-grade RAG chatbot over real energy documents.',
    fullDesc:
      'Build a production-grade Retrieval-Augmented Generation (RAG) chatbot over real energy documents. The system ingests PDF and CSV files, splits them into semantically meaningful chunks, embeds them using Azure OpenAI, and stores vectors in ChromaDB. At query time, the most relevant chunks are retrieved and injected into the LLM prompt to ground answers in real data.',
    status: 'In Progress',
    statusBg: 'bg-yellow-100',
    statusTextColor: 'text-yellow-700',
    progress: 65,
    checklist: [
      'Set up ChromaDB vector store',
      'Implement chunking strategy',
      'Test retrieval accuracy',
      'Connect to FastAPI backend',
      'Write RAGAS evaluation',
    ],
    techStack: ['Python', 'LangChain', 'ChromaDB', 'Azure OpenAI', 'FastAPI', 'RAGAS'],
    team: [
      { name: 'Devesh S.', role: 'Lead Engineer', avatar: 'DS' },
      { name: 'Aria M.', role: 'ML Engineer', avatar: 'AM' },
    ],
    timeline: [
      { date: '2026-03-01', event: 'Project kicked off' },
      { date: '2026-03-10', event: 'ChromaDB vector store live' },
      { date: '2026-03-20', event: 'Chunking strategy finalised' },
      { date: '2026-04-05', event: 'Retrieval accuracy baseline set' },
    ],
    links: [
      { label: 'GitHub Repo', url: '#' },
      { label: 'Design Doc', url: '#' },
      { label: 'RAGAS Docs', url: '#' },
    ],
  },
  {
    title: 'LangGraph Agent',
    slug: 'langgraph-agent',
    category: 'Core AI Engineering',
    color: '#10b981',
    iconBg: 'bg-emerald-100',
    iconColor: 'text-emerald-600',
    borderHover: 'hover:border-emerald-300',
    shortDesc: 'Build a stateful multi-step agent with tool use and real API calls.',
    fullDesc:
      'Build a stateful multi-step agent using LangGraph with tool use — web search, calculator, and real API calls. The agent maintains conversation memory across turns and can branch, retry, and self-correct using a graph-based execution model. Designed for complex energy domain queries requiring multiple tool invocations.',
    status: 'Not Started',
    statusBg: 'bg-gray-100',
    statusTextColor: 'text-gray-600',
    progress: 0,
    checklist: [
      'Define agent state schema',
      'Add web search tool',
      'Add calculator tool',
      'Build conversation memory',
      'Test with real queries',
    ],
    techStack: ['Python', 'LangGraph', 'LangChain', 'Tavily Search', 'Azure OpenAI'],
    team: [
      { name: 'Devesh S.', role: 'Lead Engineer', avatar: 'DS' },
    ],
    timeline: [
      { date: '2026-04-15', event: 'Kickoff planned' },
      { date: '2026-04-22', event: 'State schema design' },
      { date: '2026-05-01', event: 'Tool integrations target' },
    ],
    links: [
      { label: 'LangGraph Docs', url: '#' },
      { label: 'GitHub Repo', url: '#' },
    ],
  },
  {
    title: 'Azure Deployment',
    slug: 'azure-deployment',
    category: 'Production Systems',
    color: '#0ea5e9',
    iconBg: 'bg-sky-100',
    iconColor: 'text-sky-600',
    borderHover: 'hover:border-sky-300',
    shortDesc: 'Deploy to Azure Container Apps with full CI/CD pipeline.',
    fullDesc:
      'Deploy the chatbot to Azure Container Apps with a full GitHub Actions CI/CD pipeline spanning dev, UAT, and production environments. Infrastructure is defined as code using Bicep templates. Secrets are managed via Azure Key Vault and injected at runtime. Rollbacks are handled automatically on health-check failure.',
    status: 'Planned',
    statusBg: 'bg-blue-100',
    statusTextColor: 'text-blue-700',
    progress: 10,
    checklist: [
      'Set up Azure Container Apps',
      'Write Bicep IaC templates',
      'Configure GitHub Actions workflow',
      'Add environment secrets',
      'Test dev → UAT → prod flow',
    ],
    techStack: ['Azure Container Apps', 'GitHub Actions', 'Bicep', 'Azure Key Vault', 'Docker'],
    team: [
      { name: 'Devesh S.', role: 'DevOps Lead', avatar: 'DS' },
      { name: 'Sam K.', role: 'Cloud Architect', avatar: 'SK' },
    ],
    timeline: [
      { date: '2026-03-25', event: 'Azure subscription provisioned' },
      { date: '2026-04-20', event: 'Bicep templates target' },
      { date: '2026-05-10', event: 'CI/CD pipeline target' },
    ],
    links: [
      { label: 'Azure Portal', url: '#' },
      { label: 'Bicep Templates Repo', url: '#' },
    ],
  },
  {
    title: 'LangSmith Tracing',
    slug: 'langsmith-tracing',
    category: 'Observability',
    color: '#f97316',
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600',
    borderHover: 'hover:border-orange-300',
    shortDesc: 'Set up observability — latency, token usage, cost per query.',
    fullDesc:
      'Set up LangSmith observability across all AI pipeline stages. Track latency distributions, token usage per chain, failure rates, and cost-per-query. Configure alert rules that page on-call when error rates spike. All traces are tagged by environment and user segment for easy filtering.',
    status: 'In Progress',
    statusBg: 'bg-yellow-100',
    statusTextColor: 'text-yellow-700',
    progress: 40,
    checklist: [
      'Install LangSmith SDK',
      'Add tracing to all chains',
      'Set up project dashboard',
      'Configure cost tracking',
      'Create alert rules',
    ],
    techStack: ['LangSmith', 'Python', 'LangChain', 'Prometheus', 'PagerDuty'],
    team: [
      { name: 'Devesh S.', role: 'Observability Lead', avatar: 'DS' },
      { name: 'Priya T.', role: 'SRE', avatar: 'PT' },
    ],
    timeline: [
      { date: '2026-03-15', event: 'LangSmith account set up' },
      { date: '2026-03-28', event: 'SDK integrated into RAG pipeline' },
      { date: '2026-04-08', event: 'Cost tracking dashboard live' },
    ],
    links: [
      { label: 'LangSmith Dashboard', url: '#' },
      { label: 'Alerting Runbook', url: '#' },
    ],
  },
  {
    title: 'RAGAS Evaluation',
    slug: 'ragas-evaluation',
    category: 'Testing & Quality',
    color: '#ec4899',
    iconBg: 'bg-pink-100',
    iconColor: 'text-pink-600',
    borderHover: 'hover:border-pink-300',
    shortDesc: 'Faithfulness, relevancy, context precision metrics dashboard.',
    fullDesc:
      'Implement RAGAS evaluation metrics — faithfulness, answer relevancy, and context precision — across the full RAG pipeline. A nightly CI job re-runs the evaluation suite against a curated golden dataset and publishes a quality report. Any regression in score triggers an automatic PR comment and blocks merges.',
    status: 'Completed',
    statusBg: 'bg-green-100',
    statusTextColor: 'text-green-700',
    progress: 100,
    checklist: [
      'Install RAGAS library',
      'Define evaluation dataset',
      'Run faithfulness metrics',
      'Run relevancy metrics',
      'Build reporting dashboard',
    ],
    techStack: ['RAGAS', 'Python', 'pytest', 'GitHub Actions', 'Plotly'],
    team: [
      { name: 'Devesh S.', role: 'QA Lead', avatar: 'DS' },
      { name: 'Aria M.', role: 'ML Engineer', avatar: 'AM' },
    ],
    timeline: [
      { date: '2026-02-10', event: 'RAGAS library integrated' },
      { date: '2026-02-20', event: 'Golden dataset created (200 Q&A pairs)' },
      { date: '2026-03-05', event: 'All metrics passing baseline' },
      { date: '2026-03-12', event: 'Nightly CI job deployed' },
      { date: '2026-03-18', event: 'Completed ✓' },
    ],
    links: [
      { label: 'Evaluation Report', url: '#' },
      { label: 'GitHub Actions Job', url: '#' },
      { label: 'RAGAS Docs', url: '#' },
    ],
  },
  {
    title: 'Multi-Agent System',
    slug: 'multi-agent-system',
    category: 'AI Architecture',
    color: '#8b5cf6',
    iconBg: 'bg-violet-100',
    iconColor: 'text-violet-600',
    borderHover: 'hover:border-violet-300',
    shortDesc: 'Orchestrator + specialised sub-agents for energy domain queries.',
    fullDesc:
      'Design and build a multi-agent system with a top-level orchestrator directing specialised sub-agents: an energy data query agent (SQL + time-series), an anomaly detection agent (statistical + ML-based), and a report generation agent. The orchestrator decomposes user intent, delegates to the right sub-agent, and synthesises a final response.',
    status: 'Planned',
    statusBg: 'bg-blue-100',
    statusTextColor: 'text-blue-700',
    progress: 5,
    checklist: [
      'Design agent architecture',
      'Build orchestrator agent',
      'Build energy query agent',
      'Build anomaly detection agent',
      'Test handoff between agents',
    ],
    techStack: ['LangGraph', 'Python', 'Azure OpenAI', 'Pandas', 'scikit-learn'],
    team: [
      { name: 'Devesh S.', role: 'Architect', avatar: 'DS' },
      { name: 'Sam K.', role: 'ML Engineer', avatar: 'SK' },
      { name: 'Priya T.', role: 'Data Engineer', avatar: 'PT' },
    ],
    timeline: [
      { date: '2026-04-01', event: 'Architecture design started' },
      { date: '2026-05-15', event: 'Orchestrator prototype target' },
      { date: '2026-06-01', event: 'Sub-agents integration target' },
    ],
    links: [
      { label: 'Architecture Doc', url: '#' },
      { label: 'GitHub Repo', url: '#' },
    ],
  },
];
