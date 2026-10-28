
# AI Healthcare Project - Structure Generator
# Run from inside the AI_healthcare_project directory.
# Existing files are not overwritten.

$ErrorActionPreference = "Stop"

$directories = @(
    "docs/decisions",
    "contracts/schemas",
    "contracts/examples",
    "backend/migrations/versions",
    "backend/app/core",
    "backend/app/api/v1/endpoints",
    "backend/app/models",
    "backend/app/schemas",
    "backend/app/db",
    "backend/app/repositories",
    "backend/app/services",
    "backend/app/workers",
    "backend/tests",
    "ai-service/app/api",
    "ai-service/app/document_processing",
    "ai-service/app/xray_analysis",
    "ai-service/app/multimodal_fusion",
    "ai-service/app/rag",
    "ai-service/app/orchestration",
    "ai-service/app/common",
    "ai-service/tests",
    "ai-service/notebooks",
    "frontend",
    "data/sample-manifests",
    "scripts",
    "tests/integration",
    "tests/fixtures",
    ".github/ISSUE_TEMPLATE",
    ".github/workflows"
)

$files = @(
    "README.md",
    "LICENSE",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    ".env.example",
    "docker-compose.yml",
    "Makefile",

    "docs/project-scope.md",
    "docs/system-architecture.md",
    "docs/development-workflow.md",
    "docs/database-schema.md",
    "docs/api-specification.md",
    "docs/ai-output-contracts.md",
    "docs/security-and-privacy.md",
    "docs/testing-strategy.md",
    "docs/decisions/001-backend-framework.md",
    "docs/decisions/002-database-choice.md",
    "docs/decisions/003-ai-service-boundary.md",

    "contracts/README.md",
    "contracts/schemas/document-analysis.schema.json",
    "contracts/schemas/xray-analysis.schema.json",
    "contracts/schemas/fused-findings.schema.json",
    "contracts/schemas/chat-response.schema.json",
    "contracts/examples/document-analysis.example.json",
    "contracts/examples/xray-analysis.example.json",
    "contracts/examples/fused-findings.example.json",
    "contracts/examples/chat-response.example.json",

    "backend/README.md",
    "backend/pyproject.toml",
    "backend/alembic.ini",
    "backend/migrations/env.py",
    "backend/app/main.py",
    "backend/app/core/config.py",
    "backend/app/core/security.py",
    "backend/app/core/logging.py",
    "backend/app/api/v1/router.py",
    "backend/app/api/v1/endpoints/auth.py",
    "backend/app/api/v1/endpoints/patients.py",
    "backend/app/api/v1/endpoints/documents.py",
    "backend/app/api/v1/endpoints/analyses.py",
    "backend/app/api/v1/endpoints/chat.py",
    "backend/app/api/v1/endpoints/reports.py",
    "backend/app/models/user.py",
    "backend/app/models/patient.py",
    "backend/app/models/document.py",
    "backend/app/models/analysis.py",
    "backend/app/models/conversation.py",
    "backend/app/schemas/auth.py",
    "backend/app/schemas/patient.py",
    "backend/app/schemas/document.py",
    "backend/app/schemas/analysis.py",
    "backend/app/schemas/chat.py",
    "backend/app/db/session.py",
    "backend/app/db/base.py",
    "backend/app/services/file_storage.py",
    "backend/app/services/ai_client.py",
    "backend/app/services/report_service.py",
    "backend/tests/test_auth.py",
    "backend/tests/test_patients.py",
    "backend/tests/test_documents.py",
    "backend/tests/test_analyses.py",

    "ai-service/README.md",
    "ai-service/pyproject.toml",
    "ai-service/app/main.py",
    "ai-service/app/config.py",
    "ai-service/app/api/health.py",
    "ai-service/app/api/documents.py",
    "ai-service/app/api/images.py",
    "ai-service/app/api/fusion.py",
    "ai-service/app/api/chat.py",
    "ai-service/app/document_processing/loader.py",
    "ai-service/app/document_processing/ocr.py",
    "ai-service/app/document_processing/text_cleaning.py",
    "ai-service/app/document_processing/medical_extraction.py",
    "ai-service/app/document_processing/pipeline.py",
    "ai-service/app/xray_analysis/preprocessing.py",
    "ai-service/app/xray_analysis/model_loader.py",
    "ai-service/app/xray_analysis/inference.py",
    "ai-service/app/xray_analysis/evaluation.py",
    "ai-service/app/multimodal_fusion/normalization.py",
    "ai-service/app/multimodal_fusion/fusion.py",
    "ai-service/app/multimodal_fusion/summarization.py",
    "ai-service/app/rag/ingestion.py",
    "ai-service/app/rag/chunking.py",
    "ai-service/app/rag/embeddings.py",
    "ai-service/app/rag/retriever.py",
    "ai-service/app/rag/prompts.py",
    "ai-service/app/rag/pipeline.py",
    "ai-service/app/orchestration/workflow.py",
    "ai-service/app/common/schemas.py",
    "ai-service/app/common/exceptions.py",
    "ai-service/app/common/logging.py",
    "ai-service/tests/test_document_processing.py",
    "ai-service/tests/test_xray_analysis.py",
    "ai-service/tests/test_fusion.py",
    "ai-service/tests/test_rag.py",
    "ai-service/notebooks/document_experiments.ipynb",
    "ai-service/notebooks/xray_experiments.ipynb",

    "frontend/README.md",
    "frontend/.gitkeep",
    "data/README.md",
    "data/.gitkeep",
    "scripts/setup-dev.ps1",
    "scripts/setup-dev.sh",
    "scripts/run-backend.ps1",
    "scripts/run-ai-service.ps1",
    "scripts/check-contracts.py",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/task.md",
    ".github/workflows/tests.yml"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force |
        Out-Null
}

foreach ($file in $files) {
    $parent = Split-Path -Parent $file

    if ($parent -and !(Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force |
            Out-Null
    }

    if (!(Test-Path -LiteralPath $file)) {
        New-Item -ItemType File -Path $file |
            Out-Null
    }
}

Write-Host ""
Write-Host "AI Healthcare project structure created successfully!" `
    -ForegroundColor Green
Write-Host "Existing files have been preserved."
