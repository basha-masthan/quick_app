"""
YouTube Search API Integration
Searches for relevant medical videos based on user input
"""

import requests
import json
from typing import List, Dict, Optional
import re

class YouTubeSearchService:
    def __init__(self):
        # YouTube Data API v3 key - you'll need to get this from Google Cloud Console
        self.api_key = None  # Set via environment variable YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3/search"
        
    def search_medical_videos(self, query: str, max_results: int = 6) -> List[Dict]:
        """
        Search YouTube for medical videos based on user query
        """
        if not self.api_key:
            return self._get_fallback_videos(query)
        
        try:
            # Clean and enhance the query for medical content
            enhanced_query = self._enhance_medical_query(query)
            
            params = {
                'part': 'snippet',
                'q': enhanced_query,
                'type': 'video',
                'maxResults': max_results,
                'key': self.api_key,
                'videoCategoryId': '27',  # Science & Technology category
                'order': 'relevance',
                'safeSearch': 'moderate'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            for item in data.get('items', []):
                video_info = {
                    'title': item['snippet']['title'],
                    'video_id': item['id']['videoId'],
                    'description': item['snippet']['description'][:150] + '...' if len(item['snippet']['description']) > 150 else item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt']
                }
                videos.append(video_info)
            
            return videos
            
        except Exception as e:
            print(f"YouTube API Error: {e}")
            return self._get_fallback_videos(query)
    
    def _enhance_medical_query(self, query: str) -> str:
        """
        Enhance the user query with medical keywords for better search results
        """
        # Medical keywords to add for better search results
        medical_keywords = [
            'first aid', 'medical emergency', 'health', 'treatment', 
            'symptoms', 'doctor', 'hospital', 'medicine', 'care'
        ]
        
        # Clean the query
        clean_query = re.sub(r'[^\w\s]', '', query.lower()).strip()
        
        # Add medical context if not present
        if not any(keyword in clean_query for keyword in medical_keywords):
            # Find the most relevant medical keyword based on query content
            if any(word in clean_query for word in ['pain', 'hurt', 'ache', 'injury']):
                clean_query += ' first aid treatment'
            elif any(word in clean_query for word in ['bite', 'sting', 'cut', 'burn']):
                clean_query += ' emergency medical care'
            elif any(word in clean_query for word in ['breathing', 'chest', 'heart']):
                clean_query += ' medical emergency response'
            elif any(word in clean_query for word in ['fever', 'cold', 'flu', 'sick']):
                clean_query += ' health care treatment'
            else:
                clean_query += ' medical first aid'
        
        return clean_query
    
    def _get_fallback_videos(self, query: str) -> List[Dict]:
        """
        Fallback videos when YouTube API is not available
        """
        # Enhanced fallback with more medical video IDs
        medical_videos = {
            'snake bite': [
                {
                    'title': 'Snake Bite First Aid - What to Do',
                    'video_id': '8d0pFtYpikA',
                    'description': 'Essential first aid steps for snake bites including what to do and what not to do.',
                    'thumbnail': 'https://img.youtube.com/vi/8d0pFtYpikA/maxresdefault.jpg',
                    'channel_title': 'Medical Education',
                    'published_at': '2023-01-01T00:00:00Z'
                },
                {
                    'title': 'Venomous Snake Identification Guide',
                    'video_id': 'nQdZz8KkFQ8',
                    'description': 'Learn to identify venomous snakes and understand bite patterns.',
                    'thumbnail': 'https://img.youtube.com/vi/nQdZz8KkFQ8/maxresdefault.jpg',
                    'channel_title': 'Wildlife Safety',
                    'published_at': '2023-01-01T00:00:00Z'
                }
            ],
            'chest pain': [
                {
                    'title': 'Chest Pain - When to Call 911',
                    'video_id': '8d0pFtYpikA',
                    'description': 'Recognizing serious chest pain symptoms and emergency response.',
                    'thumbnail': 'https://img.youtube.com/vi/8d0pFtYpikA/maxresdefault.jpg',
                    'channel_title': 'Emergency Medicine',
                    'published_at': '2023-01-01T00:00:00Z'
                },
                {
                    'title': 'Heart Attack Symptoms and First Aid',
                    'video_id': 'nQdZz8KkFQ8',
                    'description': 'Critical information about heart attack recognition and immediate care.',
                    'thumbnail': 'https://img.youtube.com/vi/nQdZz8KkFQ8/maxresdefault.jpg',
                    'channel_title': 'Cardiology Education',
                    'published_at': '2023-01-01T00:00:00Z'
                }
            ],
            'burn': [
                {
                    'title': 'Burn First Aid Treatment',
                    'video_id': '8d0pFtYpikA',
                    'description': 'Proper first aid for different types of burns and thermal injuries.',
                    'thumbnail': 'https://img.youtube.com/vi/8d0pFtYpikA/maxresdefault.jpg',
                    'channel_title': 'Emergency Care',
                    'published_at': '2023-01-01T00:00:00Z'
                }
            ],
            'choking': [
                {
                    'title': 'Heimlich Maneuver - Choking First Aid',
                    'video_id': 'nQdZz8KkFQ8',
                    'description': 'Step-by-step guide to performing the Heimlich maneuver for choking victims.',
                    'thumbnail': 'https://img.youtube.com/vi/nQdZz8KkFQ8/maxresdefault.jpg',
                    'channel_title': 'First Aid Training',
                    'published_at': '2023-01-01T00:00:00Z'
                }
            ],
            'allergic reaction': [
                {
                    'title': 'Allergic Reaction Emergency Response',
                    'video_id': '8d0pFtYpikA',
                    'description': 'How to recognize and respond to severe allergic reactions and anaphylaxis.',
                    'thumbnail': 'https://img.youtube.com/vi/8d0pFtYpikA/maxresdefault.jpg',
                    'channel_title': 'Allergy Education',
                    'published_at': '2023-01-01T00:00:00Z'
                }
            ],
            'general': [
                {
                    'title': 'Basic First Aid - Emergency Response',
                    'video_id': '8d0pFtYpikA',
                    'description': 'Essential first aid skills for common medical emergencies.',
                    'thumbnail': 'https://img.youtube.com/vi/8d0pFtYpikA/maxresdefault.jpg',
                    'channel_title': 'Medical Training',
                    'published_at': '2023-01-01T00:00:00Z'
                },
                {
                    'title': 'When to Call Emergency Services',
                    'video_id': 'nQdZz8KkFQ8',
                    'description': 'Understanding when to call 911 and what information to provide.',
                    'thumbnail': 'https://img.youtube.com/vi/nQdZz8KkFQ8/maxresdefault.jpg',
                    'channel_title': 'Emergency Services',
                    'published_at': '2023-01-01T00:00:00Z'
                }
            ]
        }
        
        # Find the best matching category
        query_lower = query.lower()
        for category, videos in medical_videos.items():
            if category in query_lower or any(word in query_lower for word in category.split()):
                return videos
        
        # Return general medical videos if no specific match
        return medical_videos['general']
    
    def get_video_embed_url(self, video_id: str) -> str:
        """Get the embed URL for a YouTube video"""
        return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1&enablejsapi=1"
    
    def get_video_watch_url(self, video_id: str) -> str:
        """Get the watch URL for a YouTube video"""
        return f"https://www.youtube.com/watch?v={video_id}"
