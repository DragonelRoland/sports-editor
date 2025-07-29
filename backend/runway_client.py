import asyncio
import base64
import httpx
from pathlib import Path
from typing import Dict, Any
from config import settings
from runwayml import RunwayML, TaskFailedError

class RunwayClient:
    def __init__(self):
        # The RunwayML SDK uses RUNWAYML_API_SECRET env var by default
        # but we can also pass it directly
        import os
        os.environ['RUNWAYML_API_SECRET'] = settings.RUNWAY_API_KEY
        self.client = RunwayML()
    
    async def process_video(self, character_path: str, reference_path: str) -> Dict[str, Any]:
        """
        Process video with Runway Act Two (character performance)
        Transfers performance from reference video to character video.
        """
        try:
            print(f"🎬 Starting Act Two processing...")
            print(f"📁 Character video: {character_path}")
            print(f"📁 Reference video: {reference_path}")
            
            # Check file sizes before processing
            import os
            char_size = os.path.getsize(character_path)
            ref_size = os.path.getsize(reference_path)
            print(f"📊 Character file size: {char_size:,} bytes ({char_size/1024/1024:.2f} MB)")
            print(f"📊 Reference file size: {ref_size:,} bytes ({ref_size/1024/1024:.2f} MB)")
            
            # Upload videos to temporary hosting and get URLs
            print("🌐 Uploading character video to temporary hosting...")
            character_url = await self._upload_to_temp_host(character_path)
            print(f"✅ Character video URL: {character_url}")
            
            print("🌐 Uploading reference video to temporary hosting...")
            reference_url = await self._upload_to_temp_host(reference_path)
            print(f"✅ Reference video URL: {reference_url}")
            
            print(f"📦 Using URLs instead of base64 - much smaller payload!")
            
            # Create the Act Two task (returns immediately with task ID)
            print("🚀 Calling Runway Act Two API...")
            try:
                task_creation = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.character_performance.create(
                        model='act_two',
                                            character={
                        'type': 'video',
                        'uri': character_url,
                    },
                    reference={
                        'type': 'video', 
                        'uri': reference_url,
                    },
                        ratio='1280:720',
                        body_control=True,
                        expression_intensity=3,
                    )
                )
                print(f"✅ Task created successfully: {task_creation}")
            except Exception as api_error:
                print(f"❌ API Error: {api_error}")
                print(f"❌ Error type: {type(api_error)}")
                raise api_error
            
            # Get the task ID
            if hasattr(task_creation, 'id'):
                task_id = task_creation.id
                print(f"🎯 Task ID: {task_id}")
                
                # Now wait for completion
                print(f"⏳ Waiting for task completion...")
                try:
                    task = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.client.tasks.retrieve(task_id).wait_for_task_output()
                    )
                    print(f"📋 Task completed: {task}")
                    print(f"📋 Task status: {getattr(task, 'status', 'unknown')}")
                    print(f"📋 Task output: {getattr(task, 'output', 'none')}")
                    print(f"📋 Task error: {getattr(task, 'error', 'none')}")
                    
                    if task and hasattr(task, 'output') and task.output:
                        output_url = task.output[0] if isinstance(task.output, list) else task.output
                        print(f"✅ Got output URL: {output_url}")
                        return {
                            "success": True,
                            "video_url": output_url,
                            "task_data": task
                        }
                    else:
                        error_msg = getattr(task, 'error', 'No output video URL in response')
                        print(f"❌ No output: {error_msg}")
                        return {
                            "success": False,
                            "error": f"Task completed but no output: {error_msg}"
                        }
                except Exception as wait_error:
                    print(f"❌ Wait for completion failed: {wait_error}")
                    print(f"❌ Wait error type: {type(wait_error)}")
                    
                    # Try to get more details about the failed task
                    try:
                        print(f"🔍 Checking task status directly...")
                        task_info = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: self.client.tasks.retrieve(task_id)
                        )
                        print(f"📋 Task info: {task_info}")
                        print(f"📋 Task status: {getattr(task_info, 'status', 'unknown')}")
                        print(f"📋 Task error: {getattr(task_info, 'error', 'none')}")
                        print(f"📋 Task failure reason: {getattr(task_info, 'failure_reason', 'none')}")
                        print(f"📋 Task failure code: {getattr(task_info, 'failure_code', 'none')}")
                        
                        # Get the actual error message with helpful context
                        failure = getattr(task_info, 'failure', None)
                        failure_code = getattr(task_info, 'failure_code', None)
                        
                        if failure_code == 'NO_FACE_FOUND':
                            error_details = f"No face detected in videos.\n\nYour videos:\n• Character: {Path(character_path).name}\n• Reference: {Path(reference_path).name}\n\nOne or both videos lack detectable faces. Runway Act Two requires:\n• Front-facing faces\n• Good lighting\n• Minimal motion blur\n• Close-up or medium shots\n\nTry testing each video individually by using the same video for both character and reference to isolate which one has the issue."
                        else:
                            error_details = failure or str(wait_error)
                            
                    except Exception as info_error:
                        print(f"❌ Could not get task info: {info_error}")
                        error_details = str(wait_error)
                    
                    return {
                        "success": False,
                        "error": f"Task wait failed: {error_details}"
                    }
            else:
                return {
                    "success": False,
                    "error": "No task ID returned from API"
                }
                
        except TaskFailedError as e:
            return {
                "success": False,
                "error": f"Runway task failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}"
            }
    
    async def download_video(self, video_url: str, output_path: str) -> bool:
        """
        Download the processed video from Runway
        """
        try:
            import httpx
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
    
    async def _serve_via_ngrok(self, video_path: str) -> str:
        """Serve video via local server with ngrok tunnel"""
        import subprocess
        import json
        import time
        
        # Get the filename to serve
        filename = Path(video_path).name
        
        # Check if ngrok is already running
        try:
            result = subprocess.run(['curl', '-s', 'http://localhost:4040/api/tunnels'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                tunnels = json.loads(result.stdout)
                for tunnel in tunnels.get('tunnels', []):
                    if tunnel.get('config', {}).get('addr') == 'http://localhost:8000':
                        public_url = tunnel['public_url']
                        return f"{public_url}/serve/{filename}"
        except:
            pass
        
        # Start ngrok tunnel
        print("🚀 Starting ngrok tunnel...")
        subprocess.Popen(['ngrok', 'http', '8000'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for ngrok to start and get the public URL
        for i in range(10):  # Try for 10 seconds
            try:
                time.sleep(1)
                result = subprocess.run(['curl', '-s', 'http://localhost:4040/api/tunnels'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    tunnels = json.loads(result.stdout)
                    for tunnel in tunnels.get('tunnels', []):
                        if tunnel.get('config', {}).get('addr') == 'http://localhost:8000':
                            public_url = tunnel['public_url']
                            return f"{public_url}/serve/{filename}"
            except:
                continue
        
        raise Exception("Could not establish ngrok tunnel")
    
    async def _upload_to_temp_host(self, video_path: str) -> str:
        """Upload video to temporary file hosting service and return public URL"""
        
        # First try using local server with ngrok for reliability
        try:
            print(f"🌐 Trying local server with ngrok...")
            url = await self._serve_via_ngrok(video_path)
            print(f"✅ Successfully serving via ngrok: {url}")
            return url
        except Exception as e:
            print(f"❌ Ngrok failed: {e}")
        
        # Fallback to external services
        hosting_services = [
            self._upload_to_transfer_sh,
            self._upload_to_0x0,
            self._upload_to_fileio
        ]
        
        for service in hosting_services:
            try:
                print(f"🌐 Trying {service.__name__}...")
                url = await service(video_path)
                print(f"✅ Successfully uploaded via {service.__name__}: {url}")
                return url
            except Exception as e:
                print(f"❌ {service.__name__} failed: {e}")
                continue
        
        # If all hosting services fail, fallback to base64 for small files
        file_size = Path(video_path).stat().st_size
        if file_size < 3 * 1024 * 1024:  # Less than 3MB
            print("📦 All hosting failed, falling back to base64 for small file...")
            return self._video_to_data_uri(video_path)
        else:
            raise Exception(f"Video too large ({file_size/1024/1024:.1f}MB) and all temp hosting services failed")
    
    async def _upload_to_fileio(self, video_path: str) -> str:
        """Upload to file.io"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(video_path, 'rb') as f:
                files = {'file': f}
                response = await client.post('https://file.io', files=files)
                
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result['link']
                else:
                    raise Exception(f"File.io upload failed: {result}")
            else:
                raise Exception(f"File.io upload failed with status {response.status_code}")
    
    async def _upload_to_0x0(self, video_path: str) -> str:
        """Upload to 0x0.st (100MB limit)"""
        import time
        # Add timestamp to ensure unique uploads
        timestamp = int(time.time() * 1000)  # milliseconds
        filename = f"{timestamp}_{Path(video_path).name}"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(video_path, 'rb') as f:
                files = {'file': (filename, f, 'video/mp4')}
                response = await client.post('https://0x0.st', files=files)
                
            if response.status_code == 200:
                url = response.text.strip()
                if url.startswith('https://'):
                    return url
                else:
                    raise Exception(f"0x0.st returned invalid URL: {url}")
            else:
                raise Exception(f"0x0.st upload failed with status {response.status_code}")
    
    async def _upload_to_transfer_sh(self, video_path: str) -> str:
        """Upload to transfer.sh"""
        import time
        timestamp = int(time.time() * 1000)
        filename = f"{timestamp}_{Path(video_path).name}"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(video_path, 'rb') as f:
                headers = {'Content-Type': 'video/mp4'}
                response = await client.put(f'https://transfer.sh/{filename}', content=f, headers=headers)
                
            if response.status_code == 200:
                url = response.text.strip()
                if url.startswith('https://'):
                    return url
                else:
                    raise Exception(f"transfer.sh returned invalid URL: {url}")
            else:
                raise Exception(f"transfer.sh upload failed with status {response.status_code}")
    
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
