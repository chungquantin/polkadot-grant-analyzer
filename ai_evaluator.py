import re
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AIEvaluator:
    def __init__(self):
        self.evaluation_criteria = {
            'completeness': {
                'description': 'How complete is the proposal?',
                'weight': 0.25
            },
            'clarity': {
                'description': 'How clear and well-written is the proposal?',
                'weight': 0.20
            },
            'feasibility': {
                'description': 'How feasible is the proposed project?',
                'weight': 0.25
            },
            'impact': {
                'description': 'What is the potential impact on the ecosystem?',
                'weight': 0.20
            },
            'milestones': {
                'description': 'Are milestones well-defined and realistic?',
                'weight': 0.10
            }
        }
    
    def analyze_proposal_content(self, proposal: Dict) -> Dict:
        """Analyze proposal content and provide AI evaluation"""
        evaluation = {
            'overall_score': 0,
            'criteria_scores': {},
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'risk_level': 'LOW',
            'estimated_approval_probability': 0.0
        }
        
        title = proposal.get('title', '')
        description = proposal.get('description', '')
        milestones = proposal.get('milestones', 0)
        bounty_amount = proposal.get('bounty_amount', 0) or 0
        
        # Analyze completeness
        completeness_score = self._evaluate_completeness(title, description, milestones)
        evaluation['criteria_scores']['completeness'] = completeness_score
        
        # Analyze clarity
        clarity_score = self._evaluate_clarity(description)
        evaluation['criteria_scores']['clarity'] = clarity_score
        
        # Analyze feasibility
        feasibility_score = self._evaluate_feasibility(description, bounty_amount)
        evaluation['criteria_scores']['feasibility'] = feasibility_score
        
        # Analyze impact
        impact_score = self._evaluate_impact(description, title)
        evaluation['criteria_scores']['impact'] = impact_score
        
        # Analyze milestones
        milestones_score = self._evaluate_milestones(milestones, description)
        evaluation['criteria_scores']['milestones'] = milestones_score
        
        # Calculate overall score
        overall_score = sum(
            score * self.evaluation_criteria[criteria]['weight']
            for criteria, score in evaluation['criteria_scores'].items()
        )
        evaluation['overall_score'] = overall_score
        
        # Generate strengths and weaknesses
        evaluation['strengths'] = self._identify_strengths(evaluation['criteria_scores'])
        evaluation['weaknesses'] = self._identify_weaknesses(evaluation['criteria_scores'])
        
        # Generate recommendations
        evaluation['recommendations'] = self._generate_recommendations(evaluation['criteria_scores'])
        
        # Determine risk level
        evaluation['risk_level'] = self._determine_risk_level(overall_score, bounty_amount)
        
        # Estimate approval probability
        evaluation['estimated_approval_probability'] = self._estimate_approval_probability(overall_score)
        
        return evaluation
    
    def _evaluate_completeness(self, title: str, description: str, milestones: int) -> float:
        """Evaluate proposal completeness"""
        score = 0.0
        
        # Check title quality
        if title and len(title) > 10:
            score += 0.2
        
        # Check description length
        if description and len(description) > 500:
            score += 0.3
        elif description and len(description) > 200:
            score += 0.2
        
        # Check for key sections
        key_sections = ['objective', 'deliverables', 'timeline', 'budget', 'team']
        found_sections = sum(1 for section in key_sections if section.lower() in description.lower())
        score += (found_sections / len(key_sections)) * 0.3
        
        # Check milestones
        if milestones > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_clarity(self, description: str) -> float:
        """Evaluate proposal clarity"""
        if not description:
            return 0.0
        
        score = 0.0
        
        # Check for clear structure
        if re.search(r'##|###|#\s', description):
            score += 0.3
        
        # Check for bullet points or lists
        if re.search(r'[-*]\s|^\d+\.', description, re.MULTILINE):
            score += 0.2
        
        # Check for technical terms (indicates technical clarity)
        tech_terms = ['substrate', 'polkadot', 'parachain', 'runtime', 'pallet', 'ink', 'wasm']
        tech_count = sum(1 for term in tech_terms if term.lower() in description.lower())
        score += min(tech_count / len(tech_terms), 0.3)
        
        # Check for code examples
        if re.search(r'```|`.*`', description):
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_feasibility(self, description: str, bounty_amount: float) -> float:
        """Evaluate project feasibility"""
        score = 0.0
        
        # Check for realistic timeline
        if re.search(r'\d+\s*(week|month|day)', description, re.IGNORECASE):
            score += 0.3
        
        # Check for team information
        if re.search(r'team|developer|contributor', description, re.IGNORECASE):
            score += 0.2
        
        # Check for technical approach
        tech_approach_indicators = ['implementation', 'architecture', 'design', 'approach']
        if any(indicator in description.lower() for indicator in tech_approach_indicators):
            score += 0.2
        
        # Check bounty amount reasonableness
        if bounty_amount and bounty_amount > 0:
            if bounty_amount < 50000:  # Reasonable for most grants
                score += 0.3
            elif bounty_amount < 100000:
                score += 0.2
            else:
                score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_impact(self, description: str, title: str) -> float:
        """Evaluate potential ecosystem impact"""
        score = 0.0
        
        # Check for ecosystem keywords
        ecosystem_keywords = ['ecosystem', 'community', 'developer', 'adoption', 'integration']
        ecosystem_count = sum(1 for keyword in ecosystem_keywords 
                            if keyword.lower() in description.lower())
        score += min(ecosystem_count / len(ecosystem_keywords), 0.3)
        
        # Check for innovation indicators
        innovation_indicators = ['novel', 'innovative', 'new', 'first', 'unique']
        innovation_count = sum(1 for indicator in innovation_indicators 
                             if indicator.lower() in description.lower())
        score += min(innovation_count / len(innovation_indicators), 0.3)
        
        # Check for open source indicators
        if re.search(r'open\s*source|github|license', description, re.IGNORECASE):
            score += 0.2
        
        # Check for documentation/education value
        if re.search(r'documentation|tutorial|guide|example', description, re.IGNORECASE):
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_milestones(self, milestones: int, description: str) -> float:
        """Evaluate milestone quality"""
        score = 0.0
        
        # Check number of milestones
        if milestones >= 3:
            score += 0.4
        elif milestones >= 1:
            score += 0.2
        
        # Check for milestone descriptions in text
        if re.search(r'milestone|phase|stage', description, re.IGNORECASE):
            score += 0.3
        
        # Check for timeline information
        if re.search(r'\d+\s*(week|month)', description, re.IGNORECASE):
            score += 0.3
        
        return min(score, 1.0)
    
    def _identify_strengths(self, criteria_scores: Dict) -> List[str]:
        """Identify proposal strengths"""
        strengths = []
        
        if criteria_scores.get('completeness', 0) > 0.7:
            strengths.append("Comprehensive proposal with detailed information")
        if criteria_scores.get('clarity', 0) > 0.7:
            strengths.append("Clear and well-structured proposal")
        if criteria_scores.get('feasibility', 0) > 0.7:
            strengths.append("Realistic and achievable project plan")
        if criteria_scores.get('impact', 0) > 0.7:
            strengths.append("High potential ecosystem impact")
        if criteria_scores.get('milestones', 0) > 0.7:
            strengths.append("Well-defined milestones and timeline")
        
        return strengths
    
    def _identify_weaknesses(self, criteria_scores: Dict) -> List[str]:
        """Identify proposal weaknesses"""
        weaknesses = []
        
        if criteria_scores.get('completeness', 0) < 0.5:
            weaknesses.append("Incomplete proposal - missing key information")
        if criteria_scores.get('clarity', 0) < 0.5:
            weaknesses.append("Unclear or poorly structured proposal")
        if criteria_scores.get('feasibility', 0) < 0.5:
            weaknesses.append("Project feasibility concerns")
        if criteria_scores.get('impact', 0) < 0.5:
            weaknesses.append("Limited ecosystem impact")
        if criteria_scores.get('milestones', 0) < 0.5:
            weaknesses.append("Poorly defined milestones")
        
        return weaknesses
    
    def _generate_recommendations(self, criteria_scores: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if criteria_scores.get('completeness', 0) < 0.7:
            recommendations.append("Add more detailed project description and deliverables")
        if criteria_scores.get('clarity', 0) < 0.7:
            recommendations.append("Improve proposal structure with clear sections")
        if criteria_scores.get('feasibility', 0) < 0.7:
            recommendations.append("Provide more detailed implementation plan and timeline")
        if criteria_scores.get('impact', 0) < 0.7:
            recommendations.append("Better articulate the ecosystem impact and benefits")
        if criteria_scores.get('milestones', 0) < 0.7:
            recommendations.append("Define clear, measurable milestones with timelines")
        
        return recommendations
    
    def _determine_risk_level(self, overall_score: float, bounty_amount: float) -> str:
        """Determine project risk level"""
        if overall_score >= 0.8:
            return "LOW"
        elif overall_score >= 0.6:
            return "MEDIUM"
        elif overall_score >= 0.4:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def _estimate_approval_probability(self, overall_score: float) -> float:
        """Estimate approval probability based on score"""
        # Simple linear mapping, could be enhanced with historical data
        if overall_score >= 0.8:
            return 0.85
        elif overall_score >= 0.7:
            return 0.70
        elif overall_score >= 0.6:
            return 0.50
        elif overall_score >= 0.5:
            return 0.30
        else:
            return 0.15
    
    def analyze_proposal_files(self, proposal: Dict) -> Dict:
        """Analyze files changed in the proposal"""
        files_analysis = {
            'total_files': 0,
            'file_types': {},
            'code_files': 0,
            'documentation_files': 0,
            'complexity_score': 0.0
        }
        
        # This would require additional GitHub API calls to get file information
        # For now, we'll provide a placeholder implementation
        
        return files_analysis
    
    def generate_curator_report(self, proposal: Dict, evaluation: Dict) -> str:
        """Generate a curator-style report"""
        report = f"""
# AI Curator Report for: {proposal.get('title', 'Unknown Proposal')}

## Overall Assessment
- **Overall Score**: {evaluation['overall_score']:.2f}/1.00
- **Risk Level**: {evaluation['risk_level']}
- **Approval Probability**: {evaluation['estimated_approval_probability']:.1%}

## Detailed Evaluation

### Completeness ({evaluation['criteria_scores'].get('completeness', 0):.2f}/1.00)
{evaluation['criteria_scores'].get('completeness', 0) * 100:.0f}% - {self.evaluation_criteria['completeness']['description']}

### Clarity ({evaluation['criteria_scores'].get('clarity', 0):.2f}/1.00)
{evaluation['criteria_scores'].get('clarity', 0) * 100:.0f}% - {self.evaluation_criteria['clarity']['description']}

### Feasibility ({evaluation['criteria_scores'].get('feasibility', 0):.2f}/1.00)
{evaluation['criteria_scores'].get('feasibility', 0) * 100:.0f}% - {self.evaluation_criteria['feasibility']['description']}

### Impact ({evaluation['criteria_scores'].get('impact', 0):.2f}/1.00)
{evaluation['criteria_scores'].get('impact', 0) * 100:.0f}% - {self.evaluation_criteria['impact']['description']}

### Milestones ({evaluation['criteria_scores'].get('milestones', 0):.2f}/1.00)
{evaluation['criteria_scores'].get('milestones', 0) * 100:.0f}% - {self.evaluation_criteria['milestones']['description']}

## Strengths
{chr(10).join(f"- {strength}" for strength in evaluation['strengths']) if evaluation['strengths'] else "- None identified"}

## Areas for Improvement
{chr(10).join(f"- {weakness}" for weakness in evaluation['weaknesses']) if evaluation['weaknesses'] else "- None identified"}

## Recommendations
{chr(10).join(f"- {rec}" for rec in evaluation['recommendations']) if evaluation['recommendations'] else "- None"}

## AI Recommendation
{'APPROVE' if evaluation['estimated_approval_probability'] > 0.6 else 'REJECT' if evaluation['estimated_approval_probability'] < 0.3 else 'REVIEW_FURTHER'}
        """
        
        return report.strip() 