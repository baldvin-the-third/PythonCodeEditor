# Overview

This is an AI-powered code editor application built with Python and Streamlit that provides intelligent code suggestions, analysis, and execution capabilities across multiple programming languages (Python, JavaScript, Java, C++). The application features a web-based interface with real-time syntax highlighting, code formatting, inline suggestions, and a built-in console for code execution output. It leverages local AI services (primarily Jedi for Python) to provide context-aware code completion and analysis without requiring external API calls.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

**Problem**: Need an accessible, web-based interface for a code editor with minimal setup complexity.

**Solution**: Streamlit framework with streamlit-ace for the code editing component.

**Rationale**: Streamlit provides rapid development of web UIs with Python, while streamlit-ace integrates the Ace editor for professional code editing features. This approach eliminates the need for separate frontend/backend development and reduces deployment complexity.

**Pros**: Fast development, Python-native, easy deployment, built-in state management
**Cons**: Limited customization compared to full web frameworks, Streamlit-specific patterns required

## Backend Architecture

**Problem**: Need modular, maintainable code structure for handling multiple programming languages and services.

**Solution**: Service-oriented architecture with separate modules for AI suggestions, code execution, language handling, and code analysis.

**Key Components**:
- `AIService`: Handles code suggestions using local intelligence (Jedi for Python, pattern-based for others)
- `CodeExecutor`: Manages secure code execution with resource limits and sandboxing
- `LanguageHandler`: Provides language-specific operations (syntax validation, metrics, detection)
- `CodeAnalyzer`: Performs code quality analysis and generates refactoring suggestions

**Rationale**: Separation of concerns allows each service to evolve independently and makes testing/maintenance easier.

## Code Execution Security

**Problem**: Running arbitrary user code poses significant security risks.

**Solution**: Multi-layered security approach combining pattern-based validation and process isolation.

**Implementation**:
- `SecurityManager`: Blocks dangerous patterns (eval, exec, file operations, system imports)
- Process isolation using temporary files and subprocess execution
- Resource limits and timeouts to prevent runaway processes
- Threading locks to prevent concurrent execution conflicts

**Alternatives Considered**: Docker containers for complete isolation
**Trade-off**: Pattern-based blocking is faster but less comprehensive than containerization; acceptable for controlled environments

## AI/ML Integration Strategy

**Problem**: Need intelligent code suggestions without dependency on external paid APIs.

**Solution**: Local-first AI approach using open-source libraries.

**Implementation**:
- Python: Jedi library for AST-based code completion and analysis
- Other languages: Pattern-based suggestions and template matching
- Designed for future LLM integration (OpenAI, Hugging Face, Code Llama) with provider abstraction

**Rationale**: Immediate functionality without API costs, extensible architecture for future AI model integration.

## Language Support Architecture

**Problem**: Support multiple programming languages with different execution requirements and features.

**Solution**: Configuration-driven language support system with extensible handlers.

**Implementation**:
- Language configurations in `config/languages.py` define capabilities per language
- `LanguageHandler` provides unified interface for language-specific operations
- Separate execution methods per language in `CodeExecutor`

**Supported Languages**: Python, JavaScript, Java, C++
**Extension Path**: Add new language by defining configuration and implementing specific handlers

## State Management

**Problem**: Maintain editor state across user interactions in web environment.

**Solution**: Streamlit's session state for persistent storage of code, output, language selection, and analysis results.

**Key State Variables**:
- `code`: Current editor content
- `language`: Selected programming language
- `output`: Execution results
- `suggestions`: AI-generated code suggestions
- `analysis`: Code quality metrics and warnings

## Code Analysis Pipeline

**Problem**: Provide meaningful feedback on code quality across different languages.

**Solution**: Multi-stage analysis combining syntax validation, metrics calculation, and language-specific checks.

**Stages**:
1. Syntax validation using language-specific parsers
2. Code metrics (lines, complexity, function count)
3. Pattern-based issue detection (unused variables, missing docstrings, etc.)
4. Quality scoring based on detected issues

**Output**: Errors, warnings, suggestions, refactoring recommendations, and overall quality score

# External Dependencies

## Core Framework
- **Streamlit**: Web application framework for the UI layer
- **streamlit-ace**: Ace editor integration for code editing component

## Language Processing
- **Jedi**: Python code completion and analysis (AST-based intelligence)
- **Pygments**: Syntax highlighting across multiple languages
- **autopep8**: Python code formatting

## Code Execution
- **subprocess**: Process management for code execution
- **psutil**: Process monitoring and resource management
- **tempfile**: Temporary file creation for secure code execution

## Utilities
- **re** (regex): Pattern matching for security checks and code analysis
- **ast**: Abstract Syntax Tree parsing for Python code analysis
- **logging**: Application-level logging and error tracking

## Future Integration Points
- **OpenAI API**: For GPT/Codex-based suggestions (abstracted but not currently implemented)
- **Hugging Face API**: For alternative LLM models (abstracted but not currently implemented)
- Language-specific tools: prettier (JavaScript), eslint (JavaScript), pylint (Python)

## Runtime Requirements
- **Python 3.x**: Primary runtime environment
- **Node.js**: Required for JavaScript code execution
- **Java JDK**: Required for Java code compilation and execution
- **G++**: Required for C++ code compilation and execution