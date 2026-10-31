@echo off
setlocal
cd /d "%~dp0"

echo.
echo ==========================================
echo   MedFusion - Adding Missing Project Files
echo ==========================================
echo.

REM ==========================================
REM 1. CREATE MISSING DIRECTORIES
REM ==========================================

for %%D in (
    "backend\app\api\v1\endpoints"
    "backend\app\core"
    "backend\app\db"
    "backend\app\models"
    "backend\app\repositories"
    "backend\app\schemas"
    "backend\app\services"
    "backend\app\utils"
    "backend\tests"
    "ai-service\app\common"
    "ai-service\app\document_processing"
    "ai-service\app\xray_analysis"
    "ai-service\app\multimodal_fusion"
    "ai-service\app\rag"
    "ai-service\app\orchestration"
    "ai-service\tests"
    "contracts\schemas"
    "contracts\examples"
    "data\sample-manifests"
    "tests"
    "tests\integration"
    "tests\fixtures"
    ".github\workflows"
) do (
    if not exist "%%~D" mkdir "%%~D"
)

REM ==========================================
REM 2. BACKEND - API ENDPOINTS
REM ==========================================

for %%F in (
    "backend\app\api\v1\endpoints\users.py"
    "backend\app\api\v1\endpoints\history.py"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 3. BACKEND - DATABASE MODELS
REM ==========================================

for %%F in (
    "backend\app\models\doctor_patient.py"
    "backend\app\models\medical_record.py"
    "backend\app\models\audit_log.py"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 4. BACKEND - REPOSITORIES
REM ==========================================

for %%F in (
    "backend\app\repositories\user_repository.py"
    "backend\app\repositories\patient_repository.py"
    "backend\app\repositories\document_repository.py"
    "backend\app\repositories\analysis_repository.py"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 5. BACKEND - SCHEMAS
REM ==========================================

for %%F in (
    "backend\app\schemas\user.py"
    "backend\app\schemas\history.py"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 6. BACKEND - SERVICES
REM ==========================================

for %%F in (
    "backend\app\services\auth_service.py"
    "backend\app\services\patient_service.py"
    "backend\app\services\document_service.py"
    "backend\app\services\history_service.py"
    "backend\app\services\chat_service.py"
    "backend\app\services\pdf_service.py"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 7. BACKEND - UTILITIES AND DEPENDENCIES
REM ==========================================

for %%F in (
    "backend\app\core\dependencies.py"
    "backend\app\utils\file_validation.py"
    "backend\app\utils\exceptions.py"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 8. BACKEND - TEST FILES
REM ==========================================

for %%F in (
    "backend\tests\conftest.py"
    "backend\tests\test_auth.py"
    "backend\tests\test_patients.py"
    "backend\tests\test_documents.py"
    "backend\tests\test_history.py"
    "backend\tests\test_analyses.py"
    "backend\tests\test_permissions.py"
    "backend\tests\test_storage.py"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 9. AI SERVICE - ADDITIONAL MODULES
REM ==========================================

for %%F in (
    "ai-service\app\common\security.py"
    "ai-service\app\common\output_formatter.py"
    "ai-service\app\document_processing\output_formatter.py"
    "ai-service\app\xray_analysis\output_formatter.py"
    "ai-service\app\rag\source_attribution.py"
    "ai-service\app\orchestration\state.py"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 10. AI SERVICE - ADDITIONAL TESTS
REM ==========================================

for %%F in (
    "ai-service\tests\conftest.py"
    "ai-service\tests\test_api.py"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 11. SHARED API CONTRACTS
REM ==========================================

for %%F in (
    "contracts\schemas\upload-request.schema.json"
    "contracts\schemas\processing-status.schema.json"
    "contracts\schemas\error-response.schema.json"
    "contracts\examples\upload-request.example.json"
    "contracts\examples\processing-status.example.json"
    "contracts\examples\error-response.example.json"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 12. ROOT-LEVEL INTEGRATION TESTS
REM ==========================================

for %%F in (
    "tests\conftest.py"
    "tests\integration\test_backend_ai_integration.py"
    "tests\fixtures\.gitkeep"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 13. DEVELOPMENT CONFIGURATION
REM ==========================================

if not exist ".pre-commit-config.yaml" (
    type nul > ".pre-commit-config.yaml"
)

if not exist ".python-version" (
    > ".python-version" echo 3.12
)

REM ==========================================
REM 14. SEPARATE GITHUB TEST WORKFLOWS
REM ==========================================

for %%F in (
    ".github\workflows\backend-tests.yml"
    ".github\workflows\ai-tests.yml"
) do (
    if not exist "%%~F" type nul > "%%~F"
)

REM ==========================================
REM 15. PYTHON PACKAGE INITIALIZATION FILES
REM ==========================================

for %%D in (
    "backend\app"
    "backend\app\api"
    "backend\app\api\v1"
    "backend\app\api\v1\endpoints"
    "backend\app\core"
    "backend\app\db"
    "backend\app\models"
    "backend\app\repositories"
    "backend\app\schemas"
    "backend\app\services"
    "backend\app\utils"
    "ai-service\app"
    "ai-service\app\api"
    "ai-service\app\common"
    "ai-service\app\document_processing"
    "ai-service\app\xray_analysis"
    "ai-service\app\multimodal_fusion"
    "ai-service\app\rag"
    "ai-service\app\orchestration"
) do (
    if not exist "%%~D\__init__.py" type nul > "%%~D\__init__.py"
)

echo.
echo ==========================================
echo   Missing structure added successfully!
echo ==========================================
echo.
echo Existing files were not overwritten.
echo.
echo Next: run DIR /S to inspect your structure.
echo.

pause
endlocal