import streamlit as st
import streamlit_ace
import os
import threading
import time
from services.ai_service import AIService
from services.code_executor import CodeExecutor
from services.language_handler import LanguageHandler
from services.code_analyzer import CodeAnalyzer
from config.languages import SUPPORTED_LANGUAGES
from utils.formatters import format_code

# Initialize services
@st.cache_resource
def get_ai_service():
    return AIService()

@st.cache_resource
def get_code_executor():
    return CodeExecutor()

@st.cache_resource
def get_language_handler():
    return LanguageHandler()

@st.cache_resource
def get_code_analyzer():
    return CodeAnalyzer()

def main():
    st.set_page_config(
        page_title="AI Code Editor",
        page_icon="💻",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'code' not in st.session_state:
        st.session_state.code = SUPPORTED_LANGUAGES["python"]["sample_code"]
    if 'language' not in st.session_state:
        st.session_state.language = "python"
    if 'output' not in st.session_state:
        st.session_state.output = ""
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = []
    if 'analysis' not in st.session_state:
        st.session_state.analysis = {}
    
    # Get services
    ai_service = get_ai_service()
    code_executor = get_code_executor()
    language_handler = get_language_handler()
    code_analyzer = get_code_analyzer()
    
    # Sidebar for settings
    with st.sidebar:
        st.title("🛠️ Editor Settings")
        
        # Language selection
        selected_language = st.selectbox(
            "Programming Language",
            options=list(SUPPORTED_LANGUAGES.keys()),
            index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.language),
            key="lang_select"
        )
        
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()
        
        # AI Settings
        st.subheader("🤖 AI Settings")
        st.info("Using Local AI Models (No API required)")
        
        enable_suggestions = st.checkbox("Enable Code Suggestions", value=True)
        enable_analysis = st.checkbox("Enable Code Analysis", value=True)
        
        # Code formatting
        st.subheader("📝 Formatting")
        if st.button("Format Code", use_container_width=True):
            formatted_code = format_code(st.session_state.code, st.session_state.language)
            if formatted_code:
                st.session_state.code = formatted_code
                st.rerun()
    
    # Main interface
    st.title("🚀 AI-Powered Code Editor")
    
    # Create two columns for editor and console
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📝 Editor ({SUPPORTED_LANGUAGES[st.session_state.language]['name']})")
        
        # Code editor
        code_content = streamlit_ace.st_ace(
            value=st.session_state.code,
            language=SUPPORTED_LANGUAGES[st.session_state.language]['ace_mode'],
            theme='github',
            key='code_editor',
            height=400,
            auto_update=True,
            font_size=14,
            tab_size=4,
            wrap=True,
            markers=None,
            show_gutter=True,
            show_print_margin=True
        )
        
        # Update session state if code changed
        if code_content != st.session_state.code:
            st.session_state.code = code_content
            
            # Get AI suggestions in background
            if enable_suggestions and code_content.strip():
                with st.spinner("Analyzing code..."):
                    suggestions = ai_service.get_suggestions(
                        code_content, 
                        st.session_state.language,
                        "local"
                    )
                    st.session_state.suggestions = suggestions
            
            # Analyze code if enabled
            if enable_analysis and code_content.strip():
                analysis = code_analyzer.analyze_code(
                    code_content, 
                    st.session_state.language
                )
                st.session_state.analysis = analysis
        
        # AI Suggestions panel
        if enable_suggestions and st.session_state.suggestions:
            st.subheader("💡 AI Suggestions")
            for i, suggestion in enumerate(st.session_state.suggestions[:3]):
                with st.expander(f"Suggestion {i+1}: {suggestion.get('title', 'Code Enhancement')}"):
                    st.write(suggestion.get('description', ''))
                    if suggestion.get('code'):
                        st.code(suggestion['code'], language=st.session_state.language)
                        if st.button(f"Apply Suggestion {i+1}", key=f"apply_{i}"):
                            st.session_state.code = suggestion['code']
                            st.rerun()
        
        # Execution controls
        col_run, col_stop = st.columns(2)
        with col_run:
            if st.button("▶️ Run Code", type="primary", use_container_width=True):
                if st.session_state.code.strip():
                    with st.spinner("Executing code..."):
                        result = code_executor.execute_code(
                            st.session_state.code,
                            st.session_state.language
                        )
                        st.session_state.output = result
        
        with col_stop:
            if st.button("⏹️ Stop", use_container_width=True):
                code_executor.stop_execution()
                st.session_state.output += "\n[Execution stopped by user]"
    
    with col2:
        st.subheader("📟 Console Output")
        
        # Console output area
        console_container = st.container()
        with console_container:
            if st.session_state.output:
                st.text_area(
                    "Output",
                    value=st.session_state.output,
                    height=300,
                    disabled=True,
                    key="console_output"
                )
            else:
                st.info("Run code to see output here")
        
        # Clear console
        if st.button("🗑️ Clear Console", use_container_width=True):
            st.session_state.output = ""
            st.rerun()
        
        # Code Analysis Results
        if enable_analysis and st.session_state.analysis:
            st.subheader("🔍 Code Analysis")
            
            analysis = st.session_state.analysis
            
            # Show errors if any
            if analysis.get('errors'):
                st.error(f"Errors found: {len(analysis['errors'])}")
                for error in analysis['errors'][:3]:
                    st.write(f"❌ Line {error.get('line', 'N/A')}: {error.get('message', '')}")
            
            # Show warnings if any
            if analysis.get('warnings'):
                st.warning(f"Warnings: {len(analysis['warnings'])}")
                for warning in analysis['warnings'][:3]:
                    st.write(f"⚠️ Line {warning.get('line', 'N/A')}: {warning.get('message', '')}")
            
            # Show quality metrics
            if analysis.get('quality_score'):
                st.metric("Code Quality", f"{analysis['quality_score']}/10")
            
            # Refactoring suggestions
            if analysis.get('refactoring_suggestions'):
                with st.expander("🔧 Refactoring Suggestions"):
                    for suggestion in analysis['refactoring_suggestions'][:3]:
                        st.write(f"• {suggestion}")

if __name__ == "__main__":
    main()
