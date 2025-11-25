import os
from pathlib import Path

# -------------------------
# Define project name (main package)
# -------------------------
project_name = "src"  # More descriptive than "src"

# -------------------------
# Define additional folders
# -------------------------
cicd_folder       = "Github"
configs_folder    = "configs"
data_folder       = "data"
notebooks_folder  = "notebooks"
static_css_folder = "static/css"
templates_folder  = "templates"
tests_folder      = "tests"
scripts_folder    = "scripts"
docs_folder       = "docs"
logs_folder       = "logs"

# -------------------------
# List of files & folders to create
# -------------------------
list_of_files = [
    # Main package
    f"{project_name}/__init__.py",

    # Config
    f"{project_name}/config/__init__.py",
    f"{project_name}/config/llm_config.py",
    f"{project_name}/config/models_architecture.yaml",
    f"{project_name}/config/prompts_config.yaml",

    # Integrations for external services
    f"{project_name}/integrations/__init__.py",
    f"{project_name}/integrations/aws_integration.py",
    f"{project_name}/integrations/llms_integration.py",
    f"{project_name}/integrations/database_integration.py",
    f"{project_name}/integrations/vector_store_integration.py",


    # Constants
    f"{project_name}/constants/__init__.py",
    f"{project_name}/constants/paths.py",

    # Data access
    f"{project_name}/data_access/__init__.py",
    f"{project_name}/data_access/repository.py",
  
    # Entities
    f"{project_name}/entities/__init__.py",
    f"{project_name}/entities/artifact_entity.py",
    f"{project_name}/entities/component_entity.py",
    f"{project_name}/entities/config_entity.py",

    # Project-specific components
    f"{project_name}/components/__init__.py",
    f"{project_name}/components/data_ingestion.py",
    f"{project_name}/components/data_validation.py",
    f"{project_name}/components/data_processors.py",
    f"{project_name}/components/document_processor.py",


    # Models
    f"{project_name}/llm_models/__init__.py",
    f"{project_name}/llm_models/base_model.py",
    f"{project_name}/llm_models/openai_model.py",

    # Services
    f"{project_name}/services/__init__.py",
    f"{project_name}/services/llm_service.py",
    f"{project_name}/services/embedding_service.py",
    f"{project_name}/services/retriever_service.py",

    # LangChain
    f"{project_name}/langchain_ext/__init__.py",
    f"{project_name}/langchain_ext/llms_chat_model.py",
    f"{project_name}/langchain_ext/prompts.py",
    f"{project_name}/langchain_ext/output_parsers.py",
    f"{project_name}/langchain_ext/memory.py",
    f"{project_name}/langchain_ext/chains.py",
    f"{project_name}/langchain_ext/messages.py",
    f"{project_name}/langchain_ext/rag_retrievers.py",
    f"{project_name}/langchain_ext/embedding.py",
    f"{project_name}/langchain_ext/retrievers.py",
    f"{project_name}/langchain_ext/runnables.py",       
    f"{project_name}/langchain_ext/callbacks.py",
    f"{project_name}/langchain_ext/text_splitter.py",
    f"{project_name}/langchain_ext/tools_toolkits.py",
    f"{project_name}/langchain_ext/document_loader.py",
    f"{project_name}/langchain_ext/streaming.py",
    f"{project_name}/langchain_ext/mcp_client.py",
        
    # LangGraph
    f"{project_name}/langgraph_ext/__init__.py",
    f"{project_name}/langgraph_ext/state.py",
    f"{project_name}/langgraph_ext/nodes.py",
    f"{project_name}/langgraph_ext/edges.py",
    f"{project_name}/langgraph_ext/checkpointer.py",
    f"{project_name}/langgraph_ext/persistence.py",  
    f"{project_name}/langgraph_ext/workflows.py",
    
    # Agent
    f"{project_name}/agents/__init__.py",
    f"{project_name}/agents/base_agent.py",
    f"{project_name}/agents/planner_agent.py",
    f"{project_name}/agents/agent_executor.py",
    f"{project_name}/agents/conversational_agent.py",
    f"{project_name}/agents/tool_agent.py",
    f"{project_name}/agents/rag_agent.py",
    f"{project_name}/agents/multi_agent.py",


    # RDB / vectorstore db
    f"{project_name}/databases/__init__.py",
    f"{project_name}/databases/vector_db.py",
    f"{project_name}/databases/sqlite_db.py",

    # Pipelines
    f"{project_name}/pipelines/__init__.py",
    f"{project_name}/pipelines/training_pipeline.py",
    f"{project_name}/pipelines/inference_pipeline.py",
    f"{project_name}/pipelines/rag_pipeline.py",
    f"{project_name}/pipelines/deployment_pipeline.py",

    # Logging
    f"{project_name}/logging/__init__.py",
    f"{project_name}/logging/logger.py",

    # Exceptions
    f"{project_name}/exceptions/__init__.py",
    f"{project_name}/exceptions/exception.py",

    # Utilities
    f"{project_name}/utils/__init__.py",
    f"{project_name}/utils/handler.py",
    f"{project_name}/utils/helper.py",
    f"{project_name}/utils/app_helper.py",

    # Cloud
    f"{project_name}/cloud/__init__.py",
    f"{project_name}/cloud/aws_storage.py",

    # API
    f"{project_name}/api/__init__.py",
    f"{project_name}/api/routes.py",
    f"{project_name}/api/server.py",
    f"{project_name}/api/schemas.py",
    

    # evaluation / validation
    f"{project_name}/eval/__init__.py",
    f"{project_name}/eval/evaluator.py",
    f"{project_name}/eval/metrics.py",


    # Monitoring
    f"{project_name}/monitoring/__init__.py",
    f"{project_name}/monitoring/langsmith_logger.py",

    # Outside project_name
    f"{cicd_folder}/pipeline.yml",
    f"{configs_folder}/llms_configs.yaml",
    f"{configs_folder}/project_configs.yaml",
    f"{data_folder}/raw/.gitkeep",
    f"{notebooks_folder}/README.md",
    f"{notebooks_folder}/01_note.ipynb",
    f"{notebooks_folder}/02_note.ipynb",
    f"{templates_folder}/index.html",
    f"{static_css_folder}/style.css",

    # Scripts
    f"{scripts_folder}/automation.sh",
    f"{scripts_folder}/run_pipeline.sh",
    f"{scripts_folder}/run_pipeline.bat",

    # Tests
    f"{tests_folder}/__init__.py",
    f"{tests_folder}/conftest.py",
    f"{tests_folder}/test.py",

    # Docs
    f"{docs_folder}/architecture.md",

    # Logs folder
    f"{logs_folder}/.gitkeep",

    # Root-level files
    "requirements.txt",
    "requirements-dev.txt",
    ".env",
    "setup.py",
    ".dockerignore",
    "Dockerfile",
    "docker-compose.yml",
    "pyproject.toml",
    ".gitignore",
    "README.md",   
    "main.py",
    "demo.py",
    "app.py"
]


# -------------------------
# Create files and directories
# -------------------------
for filepath in list_of_files:
    file_path = Path(filepath)
    dir_path = file_path.parent
    os.makedirs(dir_path, exist_ok=True)
    if not file_path.exists():
        file_path.touch()
        print(f"Created: {file_path}")
    else:
        print(f"Already exists: {file_path}")
