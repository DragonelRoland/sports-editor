import httpx
import asyncio
import base64
from pathlib import Path
from typing import Dict, Any
from config import settings

class RunwayClient:
    def __init__(self):
        self.api_key = settings.RUNWAY_API_KEY
        self.base_url = "https://api.dev.runwayml.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }
    
    async def process_video(self, video_path: str, prompt: str) -> Dict[str, Any]:
        """
        Process video with Runway Act Two API
        """
        try:
            # Convert video to base64 data URI
            video_data_uri = self._video_to_data_uri(video_path)
            
            # Prepare request payload for character performance (Act Two)
            payload = {
                "promptVideo": video_data_uri,
                "promptText": prompt,
                "model": "gen4_turbo",  # Using Gen4 Turbo as it supports Act Two
                "ratio": "1280:720",    # Standard HD ratio
                "duration": 5           # Default duration
            }
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Start the character performance task
                response = await client.post(
                    f"{self.base_url}/character_performance",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"API request failed: {response.status_code} - {response.text}"
                    }
                
                task_data = response.json()
                task_id = task_data.get("id")
                
                if not task_id:
                    return {
                        "success": False,
                        "error": "No task ID returned from API"
                    }
                
                # Poll for completion
                result = await self._wait_for_completion(task_id)
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}"
            }
    
    async def _wait_for_completion(self, task_id: str) -> Dict[str, Any]:
        """
        Poll the task status until completion
        """
        max_attempts = 60  # 5 minutes with 5-second intervals
        attempt = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while attempt < max_attempts:
                try:
                    response = await client.get(
                        f"{self.base_url}/tasks/{task_id}",
                        headers=self.headers
                    )
                    
                    if response.status_code != 200:
                        return {
                            "success": False,
                            "error": f"Status check failed: {response.status_code}"
                        }
                    
                    task_data = response.json()
                    status = task_data.get("status")
                    
                    if status == "SUCCEEDED":
                        output = task_data.get("output")
                        if output and len(output) > 0:
                            return {
                                "success": True,
                                "video_url": output[0],
                                "task_data": task_data
                            }
                        else:
                            return {
                                "success": False,
                                "error": "No output video URL in response"
                            }
                    
                    elif status == "FAILED":
                        return {
                            "success": False,
                            "error": task_data.get("failure_reason", "Task failed")
                        }
                    
                    # Still processing, wait and retry
                    await asyncio.sleep(5)
                    attempt += 1
                    
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Status polling failed: {str(e)}"
                    }
        
        return {
            "success": False,
            "error": "Task timed out"
        }
    
    async def download_video(self, video_url: str, output_path: str) -> bool:
        """
        Download the processed video from Runway
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.get(video_url)
                
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    def _video_to_data_uri(self, video_path: str) -> str:
        """
        Convert video file to base64 data URI
        """
        path = Path(video_path)
        
        # Determine MIME type based on extension
        extension = path.suffix.lower()
        mime_types = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo'
        }
        
        mime_type = mime_types.get(extension, 'video/mp4')
        
        # Read and encode file
        with open(video_path, "rb") as video_file:
            video_data = video_file.read()
            base64_data = base64.b64encode(video_data).decode('utf-8')
            
        return f"data:{mime_type};base64,{base64_data}"
