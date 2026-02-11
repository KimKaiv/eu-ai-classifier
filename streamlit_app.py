"""
EU AI Act Risk Classifier - Streamlit Web App
Deploy to Streamlit Cloud for instant web interface
"""

import streamlit as st
import json
from dataclasses import asdict
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="EU AI Act Risk Classifier",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import classifier components
# Note: These will be in the same directory when deployed
try:
    from ai_act_classifier_with_search import (
        EnhancedInformationHarvestingAgent,
        RiskClassificationAgent,
        RiskLevel
    )
except ImportError:
    st.error("⚠️ Classifier modules not found. Make sure all files are in the repository.")
    st.stop()

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .risk-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .prohibited {
        background-color: #ffe6e6;
        border-left: 5px solid #ff0000;
    }
    .high-risk {
        background-color: #fff3e6;
        border-left: 5px solid #ff9900;
    }
    .transparency {
        background-color: #e6f3ff;
        border-left: 5px solid #0066cc;
    }
    .low-risk {
        background-color: #e6ffe6;
        border-left: 5px solid #00cc00;
    }
    .exception {
        background-color: #f0f0f0;
        border-left: 5px solid #999999;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<div class="main-header">EU AI Act Risk Classifier</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Classify your AI system according to the EU AI Act (2024)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">The sweet irony of using AI to assess the risk of AI -- surely not what EU legislators intended! :-)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Demonstrator under development</div>', unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This tool provides **preliminary risk classification** of AI systems according to the EU AI Act.
    
    **How it works:**
    1. Enter your AI system details
    2. AI agent analyzes the information
    3. Get classification + compliance guidance
    
    **Risk Levels:**
    - 🚫 **Prohibited** - Cannot be placed on EU market
    - ⚠️ **High-Risk** - Strict compliance required
    - ℹ️ **Transparency** - Disclosure obligations
    - ✅ **Low-Risk** - Voluntary codes of conduct
    - ➖ **Exception** - Outside AI Act scope
    """)
    
    st.markdown("---")
    
    st.header("⚖️ Legal Notice")
    st.markdown("""
    This tool provides **preliminary assessments only**.
    
    ⚠️ Not a substitute for legal advice
    
    For compliance decisions, consult qualified legal professionals.
    """)
    
    st.markdown("---")
    
    st.markdown("""
    **Version:** 1.0  
    **Last Updated:** February 2026
    """)

# Main content area
st.markdown("---")

# Create tabs
tab1, tab2, tab3 = st.tabs(["🔍 Classify System", "📚 Examples", "📖 About the EU AI Act"])

with tab1:
    st.header("Classify Your AI System")
    
    # Create form
    with st.form("classifier_form", clear_on_submit=False):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            company = st.text_input(
                "Company Name *",
                placeholder="e.g., Mercedes-Benz",
                help="Name of the organization deploying the AI system"
            )
            
            system_name = st.text_input(
                "AI System Name *",
                placeholder="e.g., MBUX Virtual Assistant",
                help="Name or identifier of the AI system"
            )
        
        with col2:
            sector = st.selectbox(
                "Sector (Optional)",
                ["Auto-detect", "Automotive", "Healthcare", "Financial Services", 
                 "Education", "Law Enforcement", "Employment", "Other"],
                help="System will auto-detect if not specified"
            )
            
            enable_search = st.checkbox(
                "Enable Web Search (Experimental)",
                value=False,
                help="Search the web for additional context (may take longer)"
            )
        
        description = st.text_area(
            "System Description *",
            placeholder="Describe what the AI system does, who uses it, and in what context...\n\nExample: An AI-powered virtual assistant that enables natural conversations with drivers, providing personalized answers for navigation and points of interest while the vehicle is in operation.",
            height=150,
            help="Provide as much detail as possible about the system's purpose, users, and deployment context"
        )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Classify System", type="primary", use_container_width=True)
    
    # Process form submission
    if submitted:
        # Validation
        if not company or not system_name or not description:
            st.error("⚠️ Please fill in all required fields (marked with *)")
        elif len(description) < 50:
            st.warning("⚠️ Please provide a more detailed description (at least 50 characters)")
        else:
            # Show progress
            with st.spinner("🔍 Analyzing your AI system..."):
                try:
                    # Stage 1: Information Harvesting
                    st.info("**Stage 1:** Harvesting information from description...")
                    
                    harvester = EnhancedInformationHarvestingAgent(enable_search=enable_search)
                    profile = harvester.harvest_from_description(
                        name=system_name,
                        company=company,
                        description=description
                    )
                    
                    # Stage 2: Risk Classification
                    st.info("**Stage 2:** Applying EU AI Act classification logic...")
                    
                    classifier = RiskClassificationAgent()
                    result = classifier.classify(profile)
                    
                    # Display results
                    st.success("✅ Classification Complete!")
                    
                    # Determine CSS class
                    css_class = {
                        RiskLevel.PROHIBITED: "prohibited",
                        RiskLevel.HIGH_RISK: "high-risk",
                        RiskLevel.TRANSPARENCY_REQUIREMENTS: "transparency",
                        RiskLevel.LOW_RISK: "low-risk",
                        RiskLevel.EXCEPTION: "exception"
                    }.get(result.risk_level, "low-risk")
                    
                    # Risk indicator
                    risk_emoji = {
                        RiskLevel.PROHIBITED: "🚫",
                        RiskLevel.HIGH_RISK: "⚠️",
                        RiskLevel.TRANSPARENCY_REQUIREMENTS: "ℹ️",
                        RiskLevel.LOW_RISK: "✅",
                        RiskLevel.EXCEPTION: "➖"
                    }.get(result.risk_level, "❓")
                    
                    # Display classification
                    st.markdown("---")
                    st.markdown(f'<div class="risk-box {css_class}">', unsafe_allow_html=True)
                    st.markdown(f"## {risk_emoji} Classification: {result.risk_level.value}")
                    st.markdown(f"**Confidence:** {result.confidence}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Create columns for detailed results
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("📊 System Profile")
                        st.markdown(f"**Sector:** {profile.sector}")
                        st.markdown(f"**Deployment:** {profile.deployment_context}")
                        st.markdown(f"**User Base:** {profile.user_base}")
                        st.markdown(f"**Decision Role:** {profile.decision_making_role}")
                        
                        if profile.biometrics_involved:
                            st.markdown(f"**🔐 Biometrics:** Yes ({profile.biometrics_purpose})")
                        
                        if profile.high_risk_context:
                            st.markdown("**⚠️ High-Risk Contexts:**")
                            for ctx in profile.high_risk_context:
                                st.markdown(f"- {ctx}")
                    
                    with col2:
                        st.subheader("💡 Reasoning")
                        for i, reason in enumerate(result.reasoning, 1):
                            st.markdown(f"{i}. {reason}")
                    
                    # Relevant provisions
                    st.subheader("📜 Relevant EU AI Act Provisions")
                    for article in result.relevant_articles:
                        st.markdown(f"- {article}")
                    
                    # Recommendations (if any)
                    if result.recommendations:
                        st.subheader("✅ Compliance Recommendations")
                        
                        # Show top 5 recommendations
                        for i, rec in enumerate(result.recommendations[:5], 1):
                            st.markdown(f"{i}. {rec}")
                        
                        if len(result.recommendations) > 5:
                            with st.expander(f"View all {len(result.recommendations)} recommendations"):
                                for i, rec in enumerate(result.recommendations[5:], 6):
                                    st.markdown(f"{i}. {rec}")
                    
                    # Export options
                    st.markdown("---")
                    st.subheader("💾 Export Results")
                    
                    # Prepare JSON export
                    export_data = {
                        "timestamp": datetime.now().isoformat(),
                        "system": {
                            "name": system_name,
                            "company": company,
                            "description": description
                        },
                        "profile": asdict(profile),
                        "classification": {
                            "risk_level": result.risk_level.value,
                            "confidence": result.confidence,
                            "reasoning": result.reasoning,
                            "relevant_articles": result.relevant_articles,
                            "recommendations": result.recommendations,
                            "decision_path": result.decision_path
                        }
                    }
                    
                    json_str = json.dumps(export_data, indent=2)
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_str,
                            file_name=f"{system_name.replace(' ', '_')}_classification.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # Generate text report
                        report = f"""EU AI ACT CLASSIFICATION REPORT
{'='*80}

System: {system_name}
Company: {company}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CLASSIFICATION: {result.risk_level.value}
Confidence: {result.confidence}

REASONING:
{chr(10).join(f'{i}. {r}' for i, r in enumerate(result.reasoning, 1))}

RELEVANT PROVISIONS:
{chr(10).join(f'- {a}' for a in result.relevant_articles)}

RECOMMENDATIONS:
{chr(10).join(f'{i}. {r}' for i, r in enumerate(result.recommendations, 1))}

{'='*80}
This is a preliminary assessment. Consult legal professionals for compliance.
"""
                        st.download_button(
                            label="📄 Download Report",
                            data=report,
                            file_name=f"{system_name.replace(' ', '_')}_report.txt",
                            mime="text/plain"
                        )
                
                except Exception as e:
                    st.error(f"❌ Error during classification: {str(e)}")
                    st.error("Please check your input and try again.")

with tab2:
    st.header("📚 Example Use Cases")
    
    st.markdown("""
    Click on any example to see how different AI systems are classified:
    """)
    
    examples = [
        {
            "name": "MBUX Virtual Assistant",
            "company": "Mercedes-Benz",
            "description": "An AI-powered virtual assistant that enables natural conversations with drivers, providing personalized answers for navigation and points of interest while the vehicle is in operation.",
            "expected": "High-Risk (Safety component in vehicle)"
        },
        {
            "name": "AI Recruitment Tool",
            "company": "HireTech Inc",
            "description": "An AI system that screens job applications, ranks candidates based on resume analysis, and recommends top candidates to hiring managers for interview selection.",
            "expected": "High-Risk (Employment decisions)"
        },
        {
            "name": "Customer Service Chatbot",
            "company": "ShopEasy",
            "description": "A conversational AI chatbot that helps customers find products, track orders, and answer frequently asked questions on our e-commerce website.",
            "expected": "Transparency Requirements (Interactive AI)"
        },
        {
            "name": "Medical Diagnosis Assistant",
            "company": "MedAI Solutions",
            "description": "An AI system that analyzes patient symptoms, medical history, and test results to suggest potential diagnoses and treatment options for physicians to review.",
            "expected": "High-Risk (Medical decision support)"
        },
        {
            "name": "Social Media Filter",
            "company": "PhotoApp",
            "description": "An AI-powered image filter that enhances photos, applies artistic effects, and removes blemishes for personal social media posts.",
            "expected": "Low-Risk (Personal use)"
        }
    ]
    
    for i, example in enumerate(examples):
        with st.expander(f"**{example['name']}** - {example['company']}"):
            st.markdown(f"**Description:** {example['description']}")
            st.markdown(f"**Expected Classification:** {example['expected']}")
            
            if st.button(f"Try this example", key=f"example_{i}"):
                st.info("Copy the details above and paste into the 'Classify System' tab!")

with tab3:
    st.header("📖 About the EU AI Act")
    
    st.markdown("""
    The **EU Artificial Intelligence Act** (AI Act) is a comprehensive legal framework regulating 
    AI systems in the European Union. It entered into force in 2024 and is the world's first 
    comprehensive AI law.
    
    ### Risk-Based Approach
    
    The AI Act uses a risk-based classification system:
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        #### 🚫 Prohibited AI Systems
        Systems that pose unacceptable risks:
        - Subliminal manipulation
        - Social scoring
        - Real-time biometric identification in public
        - Emotion recognition in workplace/schools (in most cases)
        
        #### ⚠️ High-Risk AI Systems
        Systems in sensitive areas:
        - Critical infrastructure
        - Education and employment
        - Law enforcement
        - Border control
        - Justice administration
        - Essential services (credit scoring, etc.)
        """)
    
    with col2:
        st.markdown("""
        #### ℹ️ Transparency Requirements
        Systems requiring disclosure:
        - Interactive AI (chatbots)
        - Generative AI
        - Emotion recognition systems
        - Deepfakes
        
        #### ✅ Low-Risk AI Systems
        Everything else:
        - Voluntary codes of conduct
        - No mandatory requirements
        - Encouraged to self-regulate
        """)
    
    st.markdown("---")
    
    st.subheader("Key Compliance Requirements for High-Risk Systems")
    
    st.markdown("""
    High-risk AI systems must comply with:
    
    1. **Risk Management** (Article 9) - Continuous risk assessment and mitigation
    2. **Data Governance** (Article 10) - High-quality, unbiased training data
    3. **Technical Documentation** (Article 11) - Comprehensive system documentation
    4. **Record-Keeping** (Article 12) - Logging of system operations
    5. **Transparency** (Article 13) - Clear information to users
    6. **Human Oversight** (Article 14) - Meaningful human control
    7. **Accuracy & Robustness** (Article 15) - High performance standards
    8. **Conformity Assessment** (Article 43) - Third-party evaluation
    9. **EU Database Registration** (Article 71) - Public registration
    """)
    
    st.markdown("---")
    
    st.subheader("📚 Resources")
    
    st.markdown("""
    - [Official EU AI Act Text](https://artificialintelligenceact.eu/)
    - [European Commission AI Act Page](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
    - [AI Act Compliance Guide](https://artificialintelligenceact.eu/compliance/)
    
    **Disclaimer:** This tool provides preliminary guidance only. Always consult qualified 
    legal professionals for compliance decisions.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>EU AI Act Risk Classifier v1.0</p>
    <p>⚠️ For informational purposes only. Not legal advice.</p>
    <p>Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
