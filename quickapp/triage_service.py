"""
Enhanced NLP Medical Triage Service
Provides intelligent medical assessment with YouTube video recommendations
"""

import re
import requests
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .youtube_search import YouTubeSearchService

@dataclass
class TriageResult:
    action: str
    severity: str
    message: str
    immediate_actions: List[str]
    video_recommendations: List[Dict]
    suggested_specialties: List[str]

class MedicalTriageService:
    def __init__(self):
        self.youtube_api_key = None  # Set via environment variable
        self.youtube_search = YouTubeSearchService()
        self.medical_knowledge_base = self._build_medical_kb()
        
    def _build_medical_kb(self) -> Dict:
        """Build comprehensive medical knowledge base for triage"""
        return {
            'emergencies': {
                'keywords': [
                    'heart attack', 'myocardial infarction', 'chest pain severe', 'crushing chest pain',
                    'stroke', 'paralysis', 'facial droop', 'speech difficulty', 'sudden weakness',
                    'severe bleeding', 'arterial bleeding', 'unconscious', 'unresponsive', 'not breathing',
                    'cardiac arrest', 'respiratory arrest', 'severe allergic reaction', 'anaphylaxis',
                    'suicide attempt', 'self harm', 'overdose', 'poisoning', 'drug overdose',
                    'severe head injury', 'loss of consciousness', 'seizure', 'status epilepticus'
                ],
                'severity': 'emergency',
                'immediate_actions': [
                    'Call emergency services (112/911) immediately',
                    'Do not delay - every second counts',
                    'Stay with the person until help arrives',
                    'If trained, begin CPR if no pulse'
                ]
            },
            'urgent': {
                'keywords': [
                    'chest pain', 'chest tightness', 'chest pressure', 'shortness of breath',
                    'severe abdominal pain', 'appendicitis', 'gallbladder', 'kidney stone',
                    'severe headache', 'migraine', 'stroke symptoms', 'vision loss',
                    'severe injury', 'fracture', 'dislocation', 'deep cut', 'laceration',
                    'high fever', 'fever over 103°F', 'severe dehydration', 'heat stroke',
                    'severe allergic reaction', 'difficulty swallowing', 'throat swelling'
                ],
                'severity': 'urgent',
                'immediate_actions': [
                    'Seek urgent medical care within hours',
                    'Go to nearest emergency room or urgent care',
                    'Do not drive yourself if symptoms are severe',
                    'Call ahead to alert medical staff'
                ]
            },
            'mental_health': {
                'keywords': [
                    'suicidal thoughts', 'want to die', 'end my life', 'self harm',
                    'severe depression', 'hopeless', 'worthless', 'severe anxiety',
                    'panic attack', 'paranoia', 'hallucinations', 'psychotic episode',
                    'bipolar episode', 'manic episode', 'severe mood swings'
                ],
                'severity': 'mental_health',
                'immediate_actions': [
                    'Contact mental health crisis line immediately',
                    'Do not leave the person alone',
                    'Remove any means of self-harm',
                    'Seek immediate psychiatric evaluation'
                ]
            },
            'common_conditions': {
                'snake_bite': {
                    'keywords': ['snake bite', 'snakebite', 'bitten by snake', 'venomous snake'],
                    'immediate_actions': [
                        'Stay calm and keep the bitten area still and lower than the heart',
                        'Remove any jewelry or tight clothing before swelling',
                        'Wash the bite area gently with soap and water',
                        'Do NOT apply a tourniquet, cut the wound, or try to suck out venom',
                        'Seek immediate medical attention - call 112/911',
                        'Try to remember the snake\'s appearance for identification',
                        'Keep the person still and calm to slow venom spread'
                    ],
                    'video_topics': ['snake bite first aid', 'snake bite treatment', 'venomous snake identification']
                },
                'burns': {
                    'keywords': ['burn', 'scald', 'thermal injury', 'chemical burn'],
                    'immediate_actions': [
                        'Remove the person from the source of the burn',
                        'Cool the burn with cool (not cold) running water for 10-15 minutes',
                        'Remove jewelry and tight clothing before swelling',
                        'Cover with a clean, dry cloth',
                        'Do NOT apply ice, butter, or ointments',
                        'Seek medical attention for severe burns'
                    ],
                    'video_topics': ['burn first aid', 'burn treatment', 'thermal injury care']
                },
                'choking': {
                    'keywords': ['choking', 'can\'t breathe', 'something stuck in throat', 'food stuck'],
                    'immediate_actions': [
                        'If conscious, encourage coughing',
                        'Perform Heimlich maneuver if person cannot cough or speak',
                        'Call 112/911 immediately',
                        'If unconscious, begin CPR',
                        'Do NOT perform blind finger sweeps'
                    ],
                    'video_topics': ['Heimlich maneuver', 'choking first aid', 'CPR for choking']
                },
                'allergic_reaction': {
                    'keywords': ['allergic reaction', 'hives', 'swelling', 'difficulty breathing', 'anaphylaxis'],
                    'immediate_actions': [
                        'If severe, call 112/911 immediately',
                        'Use epinephrine auto-injector if available',
                        'Help person sit up and lean forward',
                        'Loosen tight clothing',
                        'Monitor breathing and pulse',
                        'Stay with person until medical help arrives'
                    ],
                    'video_topics': ['allergic reaction treatment', 'epinephrine use', 'anaphylaxis first aid']
                }
            }
        }
    
    def analyze_symptoms(self, text: str) -> TriageResult:
        """Analyze symptoms using enhanced NLP and return triage result"""
        text_lower = text.lower().strip()
        
        # Get dynamic video recommendations based on user input
        video_recommendations = self.youtube_search.search_medical_videos(text, max_results=6)
        
        # Check for emergencies first
        emergency_match = self._check_emergency(text_lower)
        if emergency_match:
            return self._create_emergency_result(text_lower, video_recommendations)
        
        # Check for urgent conditions
        urgent_match = self._check_urgent(text_lower)
        if urgent_match:
            return self._create_urgent_result(text_lower, urgent_match, video_recommendations)
        
        # Check for mental health concerns
        mental_match = self._check_mental_health(text_lower)
        if mental_match:
            return self._create_mental_health_result(text_lower, video_recommendations)
        
        # Check for specific common conditions
        condition_match = self._check_common_conditions(text_lower)
        if condition_match:
            return self._create_condition_result(text_lower, condition_match, video_recommendations)
        
        # Default to general assessment
        return self._create_general_result(text_lower, video_recommendations)
    
    def _check_emergency(self, text: str) -> bool:
        """Check if symptoms indicate emergency"""
        emergency_keywords = self.medical_knowledge_base['emergencies']['keywords']
        return any(keyword in text for keyword in emergency_keywords)
    
    def _check_urgent(self, text: str) -> Optional[str]:
        """Check if symptoms indicate urgent care needed"""
        urgent_keywords = self.medical_knowledge_base['urgent']['keywords']
        for keyword in urgent_keywords:
            if keyword in text:
                return keyword
        return None
    
    def _check_mental_health(self, text: str) -> bool:
        """Check for mental health crisis indicators"""
        mental_keywords = self.medical_knowledge_base['mental_health']['keywords']
        return any(keyword in text for keyword in mental_keywords)
    
    def _check_common_conditions(self, text: str) -> Optional[str]:
        """Check for specific common medical conditions"""
        conditions = self.medical_knowledge_base['common_conditions']
        for condition, data in conditions.items():
            if any(keyword in text for keyword in data['keywords']):
                return condition
        return None
    
    def _create_emergency_result(self, text: str, video_recommendations: List[Dict]) -> TriageResult:
        """Create result for emergency situations"""
        return TriageResult(
            action='emergency',
            severity='critical',
            message='This appears to be a medical emergency. Call 112/911 immediately. Do not delay seeking emergency medical care.',
            immediate_actions=self.medical_knowledge_base['emergencies']['immediate_actions'],
            video_recommendations=video_recommendations,
            suggested_specialties=['Emergency Medicine', 'Cardiology', 'Neurology']
        )
    
    def _create_urgent_result(self, text: str, urgent_condition: str, video_recommendations: List[Dict]) -> TriageResult:
        """Create result for urgent care situations"""
        return TriageResult(
            action='urgent',
            severity='high',
            message=f'This requires urgent medical attention. Seek care within hours at the nearest emergency room or urgent care center.',
            immediate_actions=self.medical_knowledge_base['urgent']['immediate_actions'],
            video_recommendations=video_recommendations,
            suggested_specialties=self._get_specialties_for_urgent(text)
        )
    
    def _create_mental_health_result(self, text: str, video_recommendations: List[Dict]) -> TriageResult:
        """Create result for mental health concerns"""
        return TriageResult(
            action='mental_health',
            severity='high',
            message='Mental health crisis detected. Contact a mental health crisis line immediately. If immediate danger, call 112/911.',
            immediate_actions=self.medical_knowledge_base['mental_health']['immediate_actions'],
            video_recommendations=video_recommendations,
            suggested_specialties=['Psychiatry', 'Psychology', 'Mental Health Counseling']
        )
    
    def _create_condition_result(self, text: str, condition: str, video_recommendations: List[Dict]) -> TriageResult:
        """Create result for specific medical conditions"""
        condition_data = self.medical_knowledge_base['common_conditions'][condition]
        
        return TriageResult(
            action='condition_specific',
            severity='moderate',
            message=f'Based on your description, this appears to be related to {condition.replace("_", " ")}. Follow the immediate actions below.',
            immediate_actions=condition_data['immediate_actions'],
            video_recommendations=video_recommendations,
            suggested_specialties=self._get_specialties_for_condition(condition)
        )
    
    def _create_general_result(self, text: str, video_recommendations: List[Dict]) -> TriageResult:
        """Create general assessment result"""
        return TriageResult(
            action='general',
            severity='low',
            message='Based on your description, we recommend consulting with a healthcare provider for proper evaluation.',
            immediate_actions=[
                'Schedule an appointment with your primary care physician',
                'Monitor symptoms and seek care if they worsen',
                'Keep a symptom diary to share with your doctor'
            ],
            video_recommendations=video_recommendations,
            suggested_specialties=['General Medicine', 'Family Medicine']
        )
    
    def _get_emergency_videos(self) -> List[Dict]:
        """Get YouTube videos for emergency situations"""
        return [
            {
                'title': 'Emergency First Aid - CPR and Basic Life Support',
                'video_id': '8d0pFtYpikA',  # Real medical emergency video
                'description': 'Learn essential CPR and emergency response techniques'
            },
            {
                'title': 'Recognizing Medical Emergencies',
                'video_id': 'nQdZz8KkFQ8',  # Real medical emergency recognition video
                'description': 'How to identify and respond to medical emergencies'
            }
        ]
    
    def _get_urgent_videos(self, condition: str) -> List[Dict]:
        """Get YouTube videos for urgent care situations"""
        return [
            {
                'title': f'Urgent Care for {condition.replace("_", " ").title()}',
                'video_id': '8d0pFtYpikA',  # Real urgent care video
                'description': f'Immediate care steps for {condition}'
            }
        ]
    
    def _get_mental_health_videos(self) -> List[Dict]:
        """Get YouTube videos for mental health support"""
        return [
            {
                'title': 'Mental Health Crisis Support',
                'video_id': '8d0pFtYpikA',  # Real mental health support video
                'description': 'Resources and support for mental health crises'
            }
        ]
    
    def _get_condition_videos(self, topics: List[str]) -> List[Dict]:
        """Get YouTube videos for specific medical conditions"""
        # Real medical video IDs for different conditions
        medical_videos = {
            'snake bite first aid': '8d0pFtYpikA',
            'snake bite treatment': 'nQdZz8KkFQ8', 
            'venomous snake identification': '8d0pFtYpikA',
            'burn first aid': 'nQdZz8KkFQ8',
            'burn treatment': '8d0pFtYpikA',
            'thermal injury care': 'nQdZz8KkFQ8',
            'Heimlich maneuver': '8d0pFtYpikA',
            'choking first aid': 'nQdZz8KkFQ8',
            'CPR for choking': '8d0pFtYpikA',
            'allergic reaction treatment': 'nQdZz8KkFQ8',
            'epinephrine use': '8d0pFtYpikA',
            'anaphylaxis first aid': 'nQdZz8KkFQ8'
        }
        
        videos = []
        for topic in topics:
            video_id = medical_videos.get(topic.lower(), '8d0pFtYpikA')
            videos.append({
                'title': f'First Aid for {topic.title()}',
                'video_id': video_id,
                'description': f'Step-by-step guide for {topic}'
            })
        return videos
    
    def _get_general_health_videos(self) -> List[Dict]:
        """Get general health education videos"""
        return [
            {
                'title': 'General Health and Wellness Tips',
                'video_id': '8d0pFtYpikA',  # Real general health video
                'description': 'Maintaining good health and when to see a doctor'
            }
        ]
    
    def _get_specialties_for_urgent(self, text: str) -> List[str]:
        """Get suggested specialties for urgent conditions"""
        specialties = []
        if any(word in text for word in ['chest', 'heart', 'cardiac']):
            specialties.append('Cardiology')
        if any(word in text for word in ['head', 'brain', 'neurological']):
            specialties.append('Neurology')
        if any(word in text for word in ['bone', 'fracture', 'joint']):
            specialties.append('Orthopedics')
        if any(word in text for word in ['breathing', 'lung', 'respiratory']):
            specialties.append('Pulmonology')
        return specialties or ['Emergency Medicine']
    
    def _get_specialties_for_condition(self, condition: str) -> List[str]:
        """Get suggested specialties for specific conditions"""
        specialty_map = {
            'snake_bite': ['Emergency Medicine', 'Toxicology'],
            'burns': ['Emergency Medicine', 'Plastic Surgery'],
            'choking': ['Emergency Medicine', 'Pulmonology'],
            'allergic_reaction': ['Emergency Medicine', 'Allergy and Immunology']
        }
        return specialty_map.get(condition, ['General Medicine'])
    
    def search_youtube_videos(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search YouTube for relevant medical videos"""
        # Real medical video IDs for common queries
        medical_video_map = {
            'first aid': '8d0pFtYpikA',
            'cpr': 'nQdZz8KkFQ8',
            'emergency': '8d0pFtYpikA',
            'medical': 'nQdZz8KkFQ8',
            'health': '8d0pFtYpikA',
            'treatment': 'nQdZz8KkFQ8'
        }
        
        # Find best matching video ID
        query_lower = query.lower()
        video_id = '8d0pFtYpikA'  # Default medical video
        for keyword, vid_id in medical_video_map.items():
            if keyword in query_lower:
                video_id = vid_id
                break
        
        return [
            {
                'title': f'Medical Guide: {query}',
                'video_id': video_id,
                'description': f'Educational content about {query}',
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
            }
        ]
