import streamlit as st
import streamlit_ace
import os
import threading
import time
from services.ai_service import AIService
from services.code_executor import CodeExecutor
from services.language_handler import LanguageHandler
from services.code_analyzer import CodeAnalyzer
from services.inline_completion import InlineCompletionService
from services.smart_completion import SmartCodeCompletion
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

@st.cache_resource
def get_inline_completion():
    return InlineCompletionService()

@st.cache_resource
def get_smart_completion():
    return SmartCodeCompletion()

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
    if 'inline_suggestion' not in st.session_state:
        st.session_state.inline_suggestion = None
    if 'show_snippet_suggestions' not in st.session_state:
        st.session_state.show_snippet_suggestions = False
    
    # Get services
    ai_service = get_ai_service()
    code_executor = get_code_executor()
    language_handler = get_language_handler()
    code_analyzer = get_code_analyzer()
    inline_completion = get_inline_completion()
    smart_completion = get_smart_completion()
    
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
        enable_inline = st.checkbox("Enable Smart Inline Completions", value=True, help="AI-powered inline code predictions like Google Colab")
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
        
        # Smart inline suggestion (appears above editor like Google Colab)
        if enable_inline and st.session_state.get('smart_suggestion'):
            suggestion = st.session_state.smart_suggestion
            confidence = suggestion.get('confidence', 0) * 100
            
            # Display inline suggestion with prominent styling
            st.markdown("---")
            col_desc, col_conf, col_accept, col_reject = st.columns([3, 1, 1, 1])
            
            with col_desc:
                st.markdown(f"**✨ {suggestion.get('description', 'Code suggestion')}**")
            with col_conf:
                st.caption(f"🎯 {confidence:.0f}%")
            with col_accept:
                if st.button("✓ Accept", key="accept_smart", type="primary", use_container_width=True):
                    st.session_state.code = suggestion['completion']
                    st.session_state.smart_suggestion = None
                    st.rerun()
            with col_reject:
                if st.button("✕ Dismiss", key="reject_smart", use_container_width=True):
                    st.session_state.smart_suggestion = None
                    st.rerun()
            
            # Show suggestion in code block (inline preview)
            with st.container():
                st.code(suggestion['completion'], language=st.session_state.language, line_numbers=True)
            
            st.caption("💡 Tip: Click 'Dismiss' to reject and continue typing your own code")
            st.markdown("---")
        
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
            
            # Get smart inline completion (AI-powered)
            if enable_inline and st.session_state.language == "python":
                smart_suggestion = smart_completion.analyze_and_predict(code_content)
                st.session_state.smart_suggestion = smart_suggestion
                
                # Also get basic inline suggestion as fallback
                inline_suggestion = inline_completion.get_inline_completion(code_content)
                st.session_state.inline_suggestion = inline_suggestion
            else:
                st.session_state.smart_suggestion = None
                st.session_state.inline_suggestion = None
            
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
        
        
        # Quick snippet suggestions (inline style)
        if enable_inline:
            with st.expander("📚 Smart Code Snippets Library", expanded=False):
                st.caption("🔍 Search and insert complete code patterns")
                
                snippet_search = st.text_input(
                    "Type to search (prime, palindrome, sort, fibonacci, etc.)", 
                    key="snippet_search",
                    placeholder="Start typing..."
                )
                
                # Get smart suggestions
                if snippet_search:
                    snippets = smart_completion.get_all_suggestions(snippet_search)
                else:
                    snippets = smart_completion.get_all_suggestions("")
                
                if snippets:
                    st.caption(f"📊 Found {len(snippets)} matching patterns")
                    for idx, snippet in enumerate(snippets[:8]):
                        col_name, col_btn = st.columns([4, 1])
                        with col_name:
                            st.markdown(f"**{snippet['name']}**")
                            st.caption(snippet.get('description', ''))
                        with col_btn:
                            if st.button("Insert", key=f"snippet_{idx}", use_container_width=True):
                                st.session_state.code = snippet['code']
                                st.session_state.smart_suggestion = None
                                st.rerun()
                        
                        # Show preview
                        with st.expander(f"Preview: {snippet['name']}", expanded=False):
                            st.code(snippet['code'][:200] + "..." if len(snippet['code']) > 200 else snippet['code'], 
                                   language="python")
                        
                        if idx < len(snippets) - 1:
                            st.markdown("---")
        
        # AI Suggestions panel
        if enable_suggestions and st.session_state.suggestions:
            st.subheader("💡 AI Suggestions")
            
            # Group suggestions by type
            suggestion_types = {}
            for suggestion in st.session_state.suggestions[:10]:
                stype = suggestion.get('type', 'general')
                if stype not in suggestion_types:
                    suggestion_types[stype] = []
                suggestion_types[stype].append(suggestion)
            
            # Display by category with icons
            type_icons = {
                'algorithm': '⚙️',
                'data_structure': '📊',
                'ml_algorithm': '🤖',
                'optimization': '⚡',
                'snippet': '📝',
                'completion': '✨',
                'general': '💡'
            }
            
            for stype, suggestions in suggestion_types.items():
                icon = type_icons.get(stype, '💡')
                st.markdown(f"### {icon} {stype.replace('_', ' ').title()}")
                
                for i, suggestion in enumerate(suggestions[:3]):
                    with st.expander(f"{suggestion.get('title', 'Code Enhancement')}"):
                        st.write(suggestion.get('description', ''))
                        
                        if suggestion.get('category'):
                            st.caption(f"📂 {suggestion['category'].replace('_', ' ').title()}")
                        
                        if suggestion.get('code'):
                            st.code(suggestion['code'], language=st.session_state.language)
                            unique_key = f"apply_{stype}_{i}_{hash(suggestion['title'])}"
                            if st.button(f"Apply This", key=unique_key, use_container_width=True):
                                st.session_state.code = suggestion['code']
                                st.success(f"✅ Applied: {suggestion['title']}")
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
