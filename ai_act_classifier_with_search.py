"""
Enhanced EU AI Act Risk Classification System with Web Search
Integrates real web search to gather information about AI systems
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re

try:
    from ddgs import DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

def safe_print(msg: str):
    """Print with fallback for systems that don't support Unicode"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode('ascii'))

class RiskLevel(Enum):
    PROHIBITED = "Prohibited"
    HIGH_RISK = "High-Risk"
    LOW_RISK = "Low-Risk"
    TRANSPARENCY_REQUIREMENTS = "Additional Transparency Requirements"
    GPAI_REQUIREMENTS = "GPAI Requirements"
    EXCEPTION = "Exception"

@dataclass
class AISystemProfile:
    """Structured profile of an AI system"""
    name: str
    company: str
    description: str
    sector: str
    primary_purpose: str
    user_base: str
    biometrics_involved: bool
    biometrics_purpose: Optional[str]
    decision_making_role: str
    high_risk_context: List[str]
    data_processed: List[str]
    deployment_context: str
    additional_info: Optional[str] = None
    search_sources: List[str] = None
    
@dataclass
class ClassificationResult:
    """Result of EU AI Act classification"""
    risk_level: RiskLevel
    reasoning: List[str]
    relevant_articles: List[str]
    decision_path: List[str]
    confidence: str
    recommendations: List[str]

class EnhancedInformationHarvestingAgent:
    """
    Stage 1: Gathers information about an AI system using web search
    
    This agent:
    1. Searches for company + AI system information
    2. Analyzes search results to extract key facts
    3. Builds a comprehensive profile for classification
    """
    
    def __init__(self, enable_search: bool = True):
        self.enable_search = enable_search
        self.search_results = []
        
    def harvest_from_description(self, name: str, company: str, description: str) -> AISystemProfile:
        """
        Extract structured information using web search and analysis
        """
        safe_print(f"\n[SEARCH] Stage 1: Harvesting information for {name}")
        safe_print(f"   Company: {company}")
        
        # Step 1: Perform web searches
        search_info = ""
        sources = []
        
        if self.enable_search:
            safe_print(f"\n   Searching the web for additional context...")
            search_info, sources = self._search_for_system(name, company, description)

        # Step 2: Analyze all available information
        combined_info = f"{description}\n\nAdditional Context from Web Search:\n{search_info}"

        safe_print(f"\n   [OK] Found information from {len(sources)} sources")
        safe_print(f"   [OK] Analyzing system characteristics...")

        analysis = self._analyze_description(combined_info, name, company)

        profile = AISystemProfile(
            name=name,
            company=company,
            description=description,
            sector=analysis["sector"],
            primary_purpose=analysis["primary_purpose"],
            user_base=analysis["user_base"],
            biometrics_involved=analysis["biometrics_involved"],
            biometrics_purpose=analysis["biometrics_purpose"],
            decision_making_role=analysis["decision_making_role"],
            high_risk_context=analysis["high_risk_contexts"],
            data_processed=analysis["data_processed"],
            deployment_context=analysis["deployment_context"],
            additional_info=search_info if search_info else None,
            search_sources=sources
        )

        safe_print(f"   [OK] Profile complete!")
        
        return profile
    
    def _search_for_system(self, name: str, company: str, description: str) -> Tuple[str, List[str]]:
        """
        Perform web searches to gather additional context
        Uses DuckDuckGo search API (free, no API key required)
        """
        if not SEARCH_AVAILABLE:
            safe_print("   [WARN] Web search not available (ddgs not installed)")
            return "", []

        search_queries = [
            f"{company} {name} AI system",
            f"{company} {name} use case application",
        ]

        all_results = []
        sources = []

        try:
            with DDGS() as ddgs:
                for query in search_queries:
                    try:
                        results = list(ddgs.text(query, max_results=3))
                        for result in results:
                            # Avoid duplicates based on URL
                            if result.get('href') not in sources:
                                all_results.append({
                                    'title': result.get('title', ''),
                                    'snippet': result.get('body', ''),
                                    'url': result.get('href', '')
                                })
                                sources.append(result.get('href', ''))
                    except Exception as e:
                        safe_print(f"   [WARN] Search query failed: {e}")
                        continue
        except Exception as e:
            safe_print(f"   [WARN] Web search error: {e}")
            return "", []

        return self._format_search_results(all_results), sources
    
    def _format_search_results(self, results: List[Dict]) -> str:
        """Format search results into readable text for analysis"""
        if not results:
            return ""

        formatted = []
        for result in results:
            title = result.get('title', 'Source')
            snippet = result.get('snippet', '')
            if snippet:
                formatted.append(f"- {title}: {snippet}")

        return "\n".join(formatted)
    
    def _analyze_description(self, full_text: str, name: str, company: str) -> Dict:
        """
        Analyze the combined description and search results
        Extract key regulatory indicators
        """
        text_lower = full_text.lower()
        
        # Sector identification (enhanced with more keywords)
        sector_keywords = {
            "automotive": ["car", "vehicle", "driver", "automotive", "driving", "autonomous"],
            "healthcare": ["health", "medical", "patient", "clinical", "diagnosis", "treatment", "hospital"],
            "financial": ["bank", "finance", "credit", "loan", "mortgage", "payment", "insurance"],
            "education": ["education", "student", "learning", "school", "university", "academic"],
            "law enforcement": ["police", "law enforcement", "crime", "investigation", "surveillance"],
            "employment": ["recruitment", "hiring", "employment", "hr", "candidate", "job"],
            "critical infrastructure": ["infrastructure", "energy", "water", "electricity", "utility"],
            "border control": ["border", "migration", "asylum", "immigration", "customs"],
            "justice": ["court", "justice", "legal", "judicial", "litigation"]
        }
        
        sector = "General"
        sector_confidence = 0
        for sec, keywords in sector_keywords.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > sector_confidence:
                sector_confidence = matches
                sector = sec.title()
        
        # Biometric detection (enhanced)
        biometric_indicators = {
            "facial recognition": ["facial recognition", "face recognition", "face detection", "facial identification"],
            "fingerprint": ["fingerprint", "fingerprint scan", "fingerprint recognition"],
            "emotion recognition": ["emotion recognition", "emotion detection", "emotional state", "sentiment analysis"],
            "voice biometric": ["voice recognition", "speaker identification", "voice biometric"],
            "iris scan": ["iris scan", "iris recognition", "retinal scan"],
            "gait recognition": ["gait", "walking pattern"],
            "behavioral biometric": ["keystroke", "mouse movement", "behavioral biometric"]
        }
        
        biometrics_involved = False
        biometrics_purpose = None
        
        for bio_type, keywords in biometric_indicators.items():
            if any(kw in text_lower for kw in keywords):
                biometrics_involved = True
                
                # Determine purpose
                if "identification" in text_lower or "identify" in text_lower:
                    biometrics_purpose = "identification"
                elif "emotion" in text_lower or "sentiment" in text_lower:
                    biometrics_purpose = "emotion recognition"
                elif "categorization" in text_lower or "categorisation" in text_lower:
                    biometrics_purpose = "categorisation"
                elif "verification" in text_lower or "authenticate" in text_lower:
                    biometrics_purpose = "authentication"
                break
        
        # Decision-making role (enhanced)
        decision_indicators = {
            "Decision-making": ["decide", "decision", "approve", "reject", "determine", "evaluate", "assess", "score", "rate"],
            "Assistive/Recommendatory": ["recommend", "suggest", "assist", "advise", "guide", "help"],
            "Fully Automated Decision": ["automated decision", "automatic decision", "without human intervention"],
            "Informational": ["inform", "display", "show", "present", "visualize"]
        }
        
        decision_making_role = "Informational"
        for role, keywords in decision_indicators.items():
            if any(kw in text_lower for kw in keywords):
                decision_making_role = role
                break
        
        # High-risk contexts (comprehensive)
        high_risk_contexts = []
        risk_indicators = {
            "Safety-critical environment": ["safety", "critical", "emergency", "life-threatening"],
            "Vehicle operation": ["vehicle", "car", "driver", "driving", "autonomous vehicle", "self-driving"],
            "Medical decision": ["diagnosis", "treatment", "medical decision", "clinical decision", "patient care"],
            "Financial decision": ["credit", "loan", "financial decision", "creditworthiness", "credit score"],
            "Law enforcement": ["law enforcement", "police", "crime", "investigation", "predictive policing"],
            "Employment decision": ["recruitment", "hiring", "employment decision", "candidate selection", "performance evaluation"],
            "Educational assessment": ["exam", "grade", "admission", "educational assessment", "student evaluation"],
            "Border control": ["border", "migration", "asylum", "visa", "immigration"],
            "Justice administration": ["court", "judge", "judicial", "legal proceeding", "evidence"],
            "Essential services access": ["public benefit", "social service", "essential service", "welfare"],
            "Critical infrastructure": ["power grid", "water supply", "transportation system", "energy infrastructure"]
        }
        
        for context, keywords in risk_indicators.items():
            if any(kw in text_lower for kw in keywords):
                high_risk_contexts.append(context)
        
        # Data types processed (enhanced)
        data_types = []
        data_indicators = {
            "Personal data": ["personal", "user data", "individual data"],
            "Location data": ["location", "navigation", "gps", "geolocation"],
            "Biometric data": ["biometric", "facial", "fingerprint", "iris", "voice print"],
            "Voice/Audio data": ["voice", "speech", "audio", "conversation", "recording"],
            "Video/Image data": ["video", "camera", "image", "photograph", "visual"],
            "Financial data": ["financial", "transaction", "payment", "banking", "credit card"],
            "Health data": ["health", "medical", "clinical", "patient record", "diagnosis"],
            "Behavioral data": ["behavior", "behaviour", "pattern", "habit", "activity"],
            "Sensitive attributes": ["race", "ethnicity", "religion", "political", "sexual orientation", "health status"]
        }
        
        for data_type, keywords in data_indicators.items():
            if any(kw in text_lower for kw in keywords):
                data_types.append(data_type)
        
        # Deployment context (enhanced)
        deployment_contexts = {
            "In-vehicle system": ["vehicle", "car", "automotive", "in-car"],
            "Healthcare facility": ["hospital", "clinic", "medical facility", "healthcare"],
            "Workplace": ["workplace", "office", "work environment", "employee"],
            "Public space": ["public", "street", "outdoor", "public area"],
            "Educational institution": ["school", "university", "classroom", "campus"],
            "Border crossing": ["border", "airport", "customs", "immigration"],
            "Law enforcement": ["police station", "law enforcement", "investigation"],
            "Court/Legal": ["court", "courthouse", "legal proceeding"],
            "Online service": ["online", "web", "app", "digital", "cloud"],
            "Critical infrastructure": ["power plant", "water treatment", "infrastructure"]
        }
        
        deployment_context = "General commercial use"
        for context, keywords in deployment_contexts.items():
            if any(kw in text_lower for kw in keywords):
                deployment_context = context
                break
        
        # User base (enhanced)
        user_bases = {
            "Vehicle drivers and passengers": ["driver", "passenger", "vehicle occupant"],
            "Patients and healthcare providers": ["patient", "doctor", "nurse", "clinician", "healthcare provider"],
            "General consumers": ["customer", "consumer", "user", "client"],
            "Employees and workers": ["employee", "worker", "staff", "personnel"],
            "Students and educators": ["student", "teacher", "educator", "learner"],
            "Law enforcement officers": ["police", "officer", "law enforcement"],
            "Border control agents": ["border agent", "customs officer", "immigration officer"],
            "Judges and legal professionals": ["judge", "lawyer", "attorney", "legal professional"],
            "General public": ["public", "citizen", "resident", "population"]
        }
        
        user_base = "General public"
        for base, keywords in user_bases.items():
            if any(kw in text_lower for kw in keywords):
                user_base = base
                break
        
        # Extract primary purpose
        primary_purpose = self._extract_primary_purpose(full_text, name)
        
        return {
            "sector": sector,
            "primary_purpose": primary_purpose,
            "user_base": user_base,
            "biometrics_involved": biometrics_involved,
            "biometrics_purpose": biometrics_purpose,
            "decision_making_role": decision_making_role,
            "high_risk_contexts": high_risk_contexts,
            "data_processed": data_types,
            "deployment_context": deployment_context
        }
    
    def _extract_primary_purpose(self, text: str, name: str) -> str:
        """Extract the primary purpose from text"""
        # Try to find sentences containing the system name
        sentences = text.split(".")
        for sentence in sentences:
            if name.lower() in sentence.lower() or any(word in sentence.lower() for word in ["uses", "enables", "provides", "helps"]):
                cleaned = sentence.strip()
                if len(cleaned) > 20 and len(cleaned) < 200:
                    return cleaned
        
        # Fallback: return first substantial sentence
        for sentence in sentences:
            cleaned = sentence.strip()
            if len(cleaned) > 30:
                return cleaned[:150]
        
        return text[:150]

# Import the existing RiskClassificationAgent
class RiskClassificationAgent:
    """Stage 2: Applies EU AI Act decision logic"""
    
    def __init__(self):
        self.decision_path = []
        self.reasoning = []
        self.recommendations = []
        
    def classify(self, profile: AISystemProfile) -> ClassificationResult:
        """Apply EU AI Act flowchart logic"""
        safe_print(f"\n[CLASSIFY] Stage 2: Applying EU AI Act Classification Logic")
        
        self.decision_path = []
        self.reasoning = []
        self.recommendations = []
        
        # Check exceptions
        if self._check_exceptions(profile):
            return self._create_result(RiskLevel.EXCEPTION)
        
        # Check prohibited
        if self._check_prohibited(profile):
            return self._create_result(RiskLevel.PROHIBITED)
        
        # Check high-risk
        if self._check_high_risk(profile):
            return self._create_result(RiskLevel.HIGH_RISK)
        
        # Check transparency
        if self._check_transparency(profile):
            return self._create_result(RiskLevel.TRANSPARENCY_REQUIREMENTS)
        
        return self._create_result(RiskLevel.LOW_RISK)
    
    def _check_exceptions(self, profile: AISystemProfile) -> bool:
        """Check Article 2 exceptions"""
        self.decision_path.append("Article 2: Scope exceptions")
        
        # Scientific research
        if "research" in profile.description.lower() and "scientific" in profile.description.lower():
            self.reasoning.append("May qualify for scientific research exception (Article 2.6)")
            return True
        
        # Military/defense
        if any(word in profile.description.lower() for word in ["military", "defence", "defense"]):
            self.reasoning.append("Military/defence exception applies (Article 2.3)")
            return True
        
        return False
    
    def _check_prohibited(self, profile: AISystemProfile) -> bool:
        """Check Article 5 prohibited practices"""
        self.decision_path.append("Article 5: Prohibited AI practices")
        
        # Subliminal manipulation
        if any(word in profile.description.lower() for word in ["manipulate", "subliminal", "exploit vulnerabilities"]):
            self.reasoning.append("🚫 PROHIBITED: Subliminal manipulation (Article 5.1a)")
            return True
        
        # Social scoring
        if "social scor" in profile.description.lower():
            self.reasoning.append("🚫 PROHIBITED: Social scoring system (Article 5.1c)")
            return True
        
        # Real-time remote biometric identification
        if profile.biometrics_involved and profile.biometrics_purpose == "identification":
            if "real-time" in profile.description.lower() or "live" in profile.description.lower():
                if "public" in profile.deployment_context.lower():
                    self.reasoning.append("🚫 PROHIBITED: Real-time remote biometric identification (Article 5.1h)")
                    return True
        
        # Emotion recognition in workplace/education
        if profile.biometrics_purpose == "emotion recognition":
            if any(ctx in profile.high_risk_context for ctx in ["Workplace", "Educational assessment"]):
                self.reasoning.append("🚫 PROHIBITED: Emotion recognition in workplace/education (Article 5.1f)")
                return True
        
        return False
    
    def _check_high_risk(self, profile: AISystemProfile) -> bool:
        """Check Annex III high-risk systems"""
        self.decision_path.append("Article 6 & Annex III: High-risk systems")
        
        # Biometrics (Annex III.1)
        if profile.biometrics_involved and profile.biometrics_purpose in ["identification", "categorisation"]:
            self.reasoning.append("⚠️ HIGH-RISK: Biometric identification system (Annex III.1)")
            self._add_high_risk_recommendations("biometric")
            return True
        
        # Critical infrastructure & safety (Annex III.2)
        if "Critical infrastructure" in profile.high_risk_context:
            self.reasoning.append("⚠️ HIGH-RISK: Critical infrastructure system (Annex III.2)")
            self._add_high_risk_recommendations("infrastructure")
            return True
        
        if "Safety-critical environment" in profile.high_risk_context or "Vehicle operation" in profile.high_risk_context:
            self.reasoning.append("⚠️ HIGH-RISK: Safety component in vehicle operation (Annex III.2)")
            self.reasoning.append("System operates in safety-critical context")
            self._add_high_risk_recommendations("safety")
            return True
        
        # Education (Annex III.3)
        if "Educational assessment" in profile.high_risk_context:
            self.reasoning.append("⚠️ HIGH-RISK: Educational assessment system (Annex III.3)")
            self._add_high_risk_recommendations("education")
            return True
        
        # Employment (Annex III.4)
        if "Employment decision" in profile.high_risk_context:
            self.reasoning.append("⚠️ HIGH-RISK: Employment decision system (Annex III.4)")
            self._add_high_risk_recommendations("employment")
            return True
        
        # Essential services (Annex III.5)
        if "Essential services access" in profile.high_risk_context or "Financial decision" in profile.high_risk_context:
            self.reasoning.append("⚠️ HIGH-RISK: Essential services/creditworthiness (Annex III.5)")
            self._add_high_risk_recommendations("essential_services")
            return True
        
        # Law enforcement (Annex III.6)
        if "Law enforcement" in profile.high_risk_context:
            self.reasoning.append("⚠️ HIGH-RISK: Law enforcement application (Annex III.6)")
            self._add_high_risk_recommendations("law_enforcement")
            return True
        
        # Border control (Annex III.7)
        if "Border control" in profile.high_risk_context:
            self.reasoning.append("⚠️ HIGH-RISK: Border control system (Annex III.7)")
            self._add_high_risk_recommendations("border_control")
            return True
        
        # Justice (Annex III.8)
        if "Justice administration" in profile.high_risk_context:
            self.reasoning.append("⚠️ HIGH-RISK: Administration of justice (Annex III.8)")
            self._add_high_risk_recommendations("justice")
            return True
        
        return False
    
    def _check_transparency(self, profile: AISystemProfile) -> bool:
        """Check Article 50 transparency requirements"""
        self.decision_path.append("Article 50: Transparency requirements")
        
        # Interactive AI
        if any(word in profile.description.lower() for word in ["chat", "conversational", "assistant", "interact"]):
            self.reasoning.append("ℹ️ TRANSPARENCY: Interactive AI system (Article 50.1)")
            self.recommendations.append("Disclose AI interaction to users")
            return True
        
        # Generative AI
        if "generat" in profile.description.lower():
            self.reasoning.append("ℹ️ TRANSPARENCY: Generative AI system (Article 50.2)")
            self.recommendations.append("Label AI-generated content")
            return True
        
        return False
    
    def _add_high_risk_recommendations(self, category: str):
        """Add compliance recommendations"""
        general = [
            "Implement risk management system (Article 9)",
            "Ensure high-quality training data (Article 10)",
            "Maintain technical documentation (Article 11)",
            "Enable logging and traceability (Article 12)",
            "Implement human oversight (Article 14)",
            "Ensure accuracy and robustness (Article 15)",
            "Undergo conformity assessment (Article 43)",
            "Register in EU database (Article 71)"
        ]
        
        specific = {
            "safety": ["Conduct vehicle safety testing", "Implement fail-safe mechanisms"],
            "biometric": ["Strict biometric data access controls", "GDPR compliance"],
            "employment": ["Human-in-the-loop for decisions", "Bias testing"],
            "border_control": ["Data protection for sensitive data", "Appeal mechanisms"]
        }
        
        self.recommendations.extend(general)
        if category in specific:
            self.recommendations.extend(specific[category])
    
    def _create_result(self, risk_level: RiskLevel) -> ClassificationResult:
        """Create final result"""
        articles = {
            RiskLevel.PROHIBITED: ["Article 5 - Prohibited Practices"],
            RiskLevel.HIGH_RISK: ["Article 6 & Annex III", "Articles 8-15 - Requirements"],
            RiskLevel.TRANSPARENCY_REQUIREMENTS: ["Article 50 - Transparency"],
            RiskLevel.LOW_RISK: ["Article 69 - Codes of Conduct (voluntary)"],
            RiskLevel.EXCEPTION: ["Article 2 - Scope exceptions"]
        }
        
        confidence = "High" if len(self.reasoning) >= 3 else "Medium" if len(self.reasoning) >= 2 else "Low"
        
        return ClassificationResult(
            risk_level=risk_level,
            reasoning=self.reasoning if self.reasoning else ["No specific risks identified"],
            relevant_articles=articles.get(risk_level, []),
            decision_path=self.decision_path,
            confidence=confidence,
            recommendations=self.recommendations if self.recommendations else ["Monitor regulatory developments"]
        )

def format_result(profile: AISystemProfile, result: ClassificationResult) -> str:
    """Format results for display"""
    output = []
    output.append("\n" + "="*100)
    output.append("EU AI ACT CLASSIFICATION REPORT")
    output.append("="*100)
    
    # Profile section
    output.append("\n📋 SYSTEM PROFILE")
    output.append("─"*100)
    output.append(f"  Name: {profile.name}")
    output.append(f"  Company: {profile.company}")
    output.append(f"  Sector: {profile.sector}")
    output.append(f"  Deployment: {profile.deployment_context}")
    output.append(f"  User Base: {profile.user_base}")
    output.append(f"  Decision Role: {profile.decision_making_role}")
    
    if profile.biometrics_involved:
        output.append(f"\n  🔐 Biometrics: Yes ({profile.biometrics_purpose})")
    
    if profile.high_risk_context:
        output.append("\n  ⚠️  High-Risk Contexts:")
        for ctx in profile.high_risk_context:
            output.append(f"     • {ctx}")
    
    if profile.search_sources:
        output.append(f"\n  📚 Sources: {len(profile.search_sources)} web sources consulted")
    
    # Classification section
    indicators = {
        RiskLevel.PROHIBITED: "🚫",
        RiskLevel.HIGH_RISK: "⚠️",
        RiskLevel.TRANSPARENCY_REQUIREMENTS: "ℹ️",
        RiskLevel.LOW_RISK: "✅",
        RiskLevel.EXCEPTION: "➖"
    }
    
    output.append("\n" + "="*100)
    output.append(f"{indicators[result.risk_level]} CLASSIFICATION: {result.risk_level.value}")
    output.append(f"Confidence: {result.confidence}")
    output.append("="*100)
    
    output.append("\n💡 REASONING:")
    for i, reason in enumerate(result.reasoning, 1):
        output.append(f"  {i}. {reason}")
    
    output.append("\n📜 RELEVANT PROVISIONS:")
    for article in result.relevant_articles:
        output.append(f"  • {article}")
    
    if result.recommendations:
        output.append("\n✅ COMPLIANCE RECOMMENDATIONS:")
        for i, rec in enumerate(result.recommendations[:5], 1):  # Top 5
            output.append(f"  {i}. {rec}")
        if len(result.recommendations) > 5:
            output.append(f"  ... and {len(result.recommendations)-5} more")
    
    output.append("\n" + "="*100)
    
    return "\n".join(output)

# Example usage
if __name__ == "__main__":
    safe_print("="*100)
    safe_print("EU AI ACT CLASSIFICATION SYSTEM (with Web Search)")
    safe_print("="*100)

    # Test case
    use_case = {
        "name": "MBUX Virtual Assistant",
        "company": "Mercedes-Benz",
        "description": """Mercedes-Benz builds cars with Google AI that can talk to their drivers.
        They are using Gemini via VertexAI to power their MBUX Virtual Assistant, which enables
        natural conversations and provides personalized answers to drivers for things like navigation
        and points of interest."""
    }

    # Stage 1: Enhanced information harvesting
    harvester = EnhancedInformationHarvestingAgent(enable_search=True)
    profile = harvester.harvest_from_description(
        name=use_case["name"],
        company=use_case["company"],
        description=use_case["description"]
    )

    # Stage 2: Classification
    classifier = RiskClassificationAgent()
    result = classifier.classify(profile)

    # Display
    safe_print(format_result(profile, result))
