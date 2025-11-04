# PART 2: CORE PLUGIN IMPLEMENTATIONS

## 5. LLM Manager Plugin (Alternative Implementation)

### Design Goals
1. **Hot-swappable** - Switch between Ollama, GPT4All, OpenAI, etc. without code changes
2. **Fallback system** - If primary LLM fails, try secondary
3. **Token tracking** - Monitor usage for performance analysis
4. **Streaming support** - Real-time response generation
5. **Five Lenses integration** - Every response passes through ethical processing

### LLM Plugin Implementation

```python
# File: plugins/ollama_plugin.py
"""
Ollama LLM Plugin
Implements hot-swappable LLM interface for Ollama
"""

import requests
import time
from typing import Dict, Any, List, Generator
import logging

from core.plugin_base import BasePlugin, PluginMetadata
from core.message_bus import MessageBus, Event

logger = logging.getLogger(__name__)


class OllamaPlugin(BasePlugin):
    """
    Ollama LLM plugin - connects to local Ollama instance.
    
    Subscribes to: 'llm_request'
    Publishes: 'llm_response', 'llm_error'
    """
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="OllamaLLM",
            version="1.0.0",
            description="Local LLM via Ollama",
            author="Raven Core Team",
            capabilities=["text_generation", "streaming", "chat"],
            dependencies=[]
        )
    
    def initialize(self) -> bool:
        """
        Initialize connection to Ollama.
        """
        try:
            self.base_url = self.config.get('base_url', 'http://localhost:11434')
            self.model_name = self.config.get('model_name', 'llama3.2:3b')
            self.temperature = self.config.get('temperature', 0.7)
            self.max_tokens = self.config.get('max_tokens', 2048)
            self.context_window = self.config.get('context_window', 4096)
            
            # Test connection
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = [m['name'] for m in response.json().get('models', [])]
                
                if self.model_name not in available_models:
                    logger.warning(f"Model {self.model_name} not found. Available: {available_models}")
                    return False
                
                logger.info(f"Ollama connected. Using model: {self.model_name}")
                
                # Subscribe to LLM requests
                self.subscribe('llm_request', self.handle_llm_request)
                
                return True
            else:
                logger.error("Failed to connect to Ollama")
                return False
                
        except Exception as e:
            logger.error(f"Ollama initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """
        Cleanup Ollama connection.
        """
        logger.info("Ollama plugin shutdown")
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if Ollama is responding.
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'message': 'Ollama responding',
                    'model': self.model_name
                }
        except:
            pass
        
        return {
            'status': 'unhealthy',
            'message': 'Ollama not responding'
        }
    
    def handle_llm_request(self, event: Event):
        """
        Handle incoming LLM request event.
        
        Event data should contain:
        - prompt: str
        - system_prompt: Optional[str]
        - temperature: Optional[float]
        - max_tokens: Optional[int]
        - stream: Optional[bool]
        """
        if not self.enabled:
            return
        
        try:
            prompt = event.data.get('prompt', '')
            system_prompt = event.data.get('system_prompt')
            temperature = event.data.get('temperature', self.temperature)
            max_tokens = event.data.get('max_tokens', self.max_tokens)
            stream = event.data.get('stream', False)
            
            if stream:
                # Streaming response
                response_generator = self._generate_stream(
                    prompt, system_prompt, temperature, max_tokens
                )
                self.publish('llm_stream_start', {
                    'request_id': event.data.get('request_id')
                })
                
                for chunk in response_generator:
                    self.publish('llm_stream_chunk', {
                        'chunk': chunk,
                        'request_id': event.data.get('request_id')
                    })
                
                self.publish('llm_stream_end', {
                    'request_id': event.data.get('request_id')
                })
            else:
                # Regular response
                response = self._generate(
                    prompt, system_prompt, temperature, max_tokens
                )
                
                self.publish('llm_response', {
                    'text': response['text'],
                    'tokens_used': response['tokens_used'],
                    'latency_ms': response['latency_ms'],
                    'model': self.model_name,
                    'request_id': event.data.get('request_id')
                }, priority=2)
                
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            self.publish('llm_error', {
                'error': str(e),
                'request_id': event.data.get('request_id')
            })
    
    def _generate(self, prompt: str, system_prompt: str = None,
                  temperature: float = None, max_tokens: int = None) -> Dict[str, Any]:
        """
        Generate completion from Ollama.
        """
        start_time = time.time()
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        # Make request to Ollama
        payload = {
            'model': self.model_name,
            'messages': messages,
            'temperature': temperature or self.temperature,
            'options': {
                'num_predict': max_tokens or self.max_tokens
            },
            'stream': False
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            text = data['message']['content']
            tokens = data.get('eval_count', 0) + data.get('prompt_eval_count', 0)
            latency = (time.time() - start_time) * 1000
            
            return {
                'text': text,
                'tokens_used': tokens,
                'latency_ms': latency
            }
        else:
            raise Exception(f"Ollama request failed: {response.status_code}")
    
    def _generate_stream(self, prompt: str, system_prompt: str = None,
                        temperature: float = None, max_tokens: int = None) -> Generator[str, None, None]:
        """
        Generate streaming completion from Ollama.
        """
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        
        payload = {
            'model': self.model_name,
            'messages': messages,
            'temperature': temperature or self.temperature,
            'options': {'num_predict': max_tokens or self.max_tokens},
            'stream': True
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=120
        )
        
        for line in response.iter_lines():
            if line:
                import json
                data = json.loads(line)
                if 'message' in data and 'content' in data['message']:
                    yield data['message']['content']
```

### Alternative: GPT4All Plugin

```python
# File: plugins/gpt4all_plugin.py
"""
GPT4All LLM Plugin - Alternative to Ollama
This shows how easy it is to swap LLMs
"""

from pathlib import Path
import time
import os
from typing import Dict, Any
import logging

# Set CPU mode before importing gpt4all
os.environ.setdefault("GGML_NO_CUDA", "1")
os.environ.setdefault("LLAMA_CUBLAS", "0")

try:
    from gpt4all import GPT4All
except ImportError:
    GPT4All = None

from core.plugin_base import BasePlugin, PluginMetadata
from core.message_bus import MessageBus, Event

logger = logging.getLogger(__name__)


class Gpt4allPlugin(BasePlugin):
    """
    GPT4All LLM plugin - runs GGUF models locally.
    
    Same interface as Ollama plugin - can be swapped via config.
    
    Subscribes to: 'llm_request'
    Publishes: 'llm_response', 'llm_error'
    """
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="GPT4AllLLM",
            version="1.0.0",
            description="Local LLM via GPT4All (GGUF models)",
            author="Raven Core Team",
            capabilities=["text_generation", "streaming"],
            dependencies=["gpt4all"]
        )
    
    def initialize(self) -> bool:
        """
        Initialize GPT4All model.
        """
        if GPT4All is None:
            logger.error("gpt4all package not installed")
            return False
        
        try:
            model_path = Path(self.config.get('model_path', './models'))
            model_name = self.config.get('model_name', 'Phi-3.5-mini-instruct_Uncensored-Q4_K_M.gguf')
            self.n_threads = self.config.get('n_threads', 6)
            self.temperature = self.config.get('temperature', 0.3)
            self.max_tokens = self.config.get('max_tokens', 512)
            
            full_path = model_path / model_name
            
            if not full_path.exists():
                logger.error(f"Model not found: {full_path}")
                return False
            
            # Load model
            self.model = GPT4All(
                model_name=model_name,
                model_path=str(model_path),
                allow_download=False
            )
            
            # Set thread count
            try:
                self.model.model.set_thread_count(self.n_threads)
            except:
                pass
            
            logger.info(f"GPT4All loaded: {model_name}")
            
            # Subscribe to LLM requests
            self.subscribe('llm_request', self.handle_llm_request)
            
            return True
            
        except Exception as e:
            logger.error(f"GPT4All initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """
        Cleanup GPT4All model.
        """
        if hasattr(self, 'model'):
            del self.model
        logger.info("GPT4All plugin shutdown")
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if model is loaded.
        """
        if hasattr(self, 'model') and self.model:
            return {
                'status': 'healthy',
                'message': 'GPT4All model loaded',
                'threads': self.n_threads
            }
        return {
            'status': 'unhealthy',
            'message': 'Model not loaded'
        }
    
    def handle_llm_request(self, event: Event):
        """
        Handle incoming LLM request event.
        """
        if not self.enabled:
            return
        
        try:
            prompt = event.data.get('prompt', '')
            system_prompt = event.data.get('system_prompt')
            temperature = event.data.get('temperature', self.temperature)
            max_tokens = event.data.get('max_tokens', self.max_tokens)
            
            response = self._generate(prompt, system_prompt, temperature, max_tokens)
            
            self.publish('llm_response', {
                'text': response['text'],
                'tokens_used': response['tokens_used'],
                'latency_ms': response['latency_ms'],
                'model': self.config.get('model_name'),
                'request_id': event.data.get('request_id')
            }, priority=2)
            
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            self.publish('llm_error', {
                'error': str(e),
                'request_id': event.data.get('request_id')
            })
    
    def _generate(self, prompt: str, system_prompt: str = None,
                  temperature: float = None, max_tokens: int = None) -> Dict[str, Any]:
        """
        Generate completion from GPT4All.
        """
        start_time = time.time()
        
        # Build full prompt
        full_prompt = ""
        if system_prompt:
            full_prompt = f"SYSTEM: {system_prompt}\n\nUSER: {prompt}\nASSISTANT:"
        else:
            full_prompt = f"USER: {prompt}\nASSISTANT:"
        
        # Generate
        try:
            text = self.model.generate(
                full_prompt,
                max_tokens=max_tokens or self.max_tokens,
                temp=temperature or self.temperature,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1
            )
            
            # Clean up output
            text = (text or "").strip()
            
            # Estimate tokens (rough)
            tokens_used = len(text.split()) + len(prompt.split())
            latency = (time.time() - start_time) * 1000
            
            return {
                'text': text,
                'tokens_used': tokens_used,
                'latency_ms': latency
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
```

### LLM Coordinator (Fallback System)

```python
# File: plugins/llm_coordinator_plugin.py
"""
LLM Coordinator - manages multiple LLM plugins with fallback
This ensures the system keeps working even if one LLM fails
"""

import logging
from typing import Dict, Any, List
import uuid

from core.plugin_base import BasePlugin, PluginMetadata
from core.message_bus import MessageBus, Event

logger = logging.getLogger(__name__)


class LlmCoordinatorPlugin(BasePlugin):
    """
    Coordinates multiple LLM plugins.
    
    If primary LLM fails, automatically tries fallback.
    Tracks performance and can switch based on speed/reliability.
    
    Subscribes to: 'user_input_processed'
    Publishes: 'llm_request', 'llm_final_response'
    """
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="LLMCoordinator",
            version="1.0.0",
            description="Coordinates LLM plugins with fallback",
            author="Raven Core Team",
            capabilities=["llm_management", "fallback", "performance_tracking"]
        )
    
    def initialize(self) -> bool:
        """
        Initialize LLM coordinator.
        """
        self.primary_llm = self.config.get('primary_llm', 'OllamaLLM')
        self.fallback_llm = self.config.get('fallback_llm', 'GPT4AllLLM')
        self.timeout = self.config.get('timeout', 30.0)
        
        self.pending_requests: Dict[str, Dict] = {}
        self.performance_stats: Dict[str, List[float]] = {
            self.primary_llm: [],
            self.fallback_llm: []
        }
        
        # Subscribe to events
        self.subscribe('user_input_processed', self.handle_user_input)
        self.subscribe('llm_response', self.handle_llm_response)
        self.subscribe('llm_error', self.handle_llm_error)
        
        logger.info(f"LLM Coordinator initialized (primary: {self.primary_llm}, fallback: {self.fallback_llm})")
        return True
    
    def shutdown(self) -> bool:
        """
        Cleanup coordinator.
        """
        logger.info("LLM Coordinator shutdown")
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check coordinator health.
        """
        return {
            'status': 'healthy',
            'message': 'LLM Coordinator operational',
            'primary': self.primary_llm,
            'fallback': self.fallback_llm,
            'pending_requests': len(self.pending_requests)
        }
    
    def handle_user_input(self, event: Event):
        """
        User input has been processed - send to LLM.
        """
        if not self.enabled:
            return
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Store request info
        self.pending_requests[request_id] = {
            'prompt': event.data.get('prompt'),
            'system_prompt': event.data.get('system_prompt'),
            'attempted_llms': [],
            'timestamp': event.timestamp
        }
        
        # Send to primary LLM
        self._send_to_llm(request_id, self.primary_llm)
    
    def _send_to_llm(self, request_id: str, llm_name: str):
        """
        Send request to specific LLM.
        """
        if request_id not in self.pending_requests:
            return
        
        request_data = self.pending_requests[request_id]
        request_data['attempted_llms'].append(llm_name)
        
        logger.info(f"Sending request {request_id} to {llm_name}")
        
        self.publish('llm_request', {
            'request_id': request_id,
            'prompt': request_data['prompt'],
            'system_prompt': request_data['system_prompt'],
            'target_llm': llm_name
        }, priority=2)
    
    def handle_llm_response(self, event: Event):
        """
        LLM responded successfully.
        """
        request_id = event.data.get('request_id')
        
        if request_id in self.pending_requests:
            # Track performance
            latency = event.data.get('latency_ms', 0)
            model = event.data.get('model', event.source)
            
            if model in self.performance_stats:
                self.performance_stats[model].append(latency)
                # Keep last 100 measurements
                self.performance_stats[model] = self.performance_stats[model][-100:]
            
            # Clean up
            del self.pending_requests[request_id]
            
            # Forward to next stage (Five Lenses processing)
            self.publish('llm_final_response', {
                'text': event.data.get('text'),
                'tokens_used': event.data.get('tokens_used'),
                'latency_ms': latency,
                'model': model
            }, priority=2)
    
    def handle_llm_error(self, event: Event):
        """
        LLM failed - try fallback.
        """
        request_id = event.data.get('request_id')
        
        if request_id not in self.pending_requests:
            return
        
        request_data = self.pending_requests[request_id]
        
        logger.warning(f"LLM error for request {request_id}: {event.data.get('error')}")
        
        # Try fallback if we haven't already
        if self.fallback_llm not in request_data['attempted_llms']:
            logger.info(f"Trying fallback LLM: {self.fallback_llm}")
            self._send_to_llm(request_id, self.fallback_llm)
        else:
            # All LLMs failed
            logger.error(f"All LLMs failed for request {request_id}")
            del self.pending_requests[request_id]
            
            # Publish failure event
            self.publish('llm_complete_failure', {
                'request_id': request_id,
                'error': 'All LLM engines failed'
            }, priority=1)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get LLM performance statistics.
        """
        stats = {}
        for llm, latencies in self.performance_stats.items():
            if latencies:
                stats[llm] = {
                    'avg_latency_ms': sum(latencies) / len(latencies),
                    'min_latency_ms': min(latencies),
                    'max_latency_ms': max(latencies),
                    'sample_count': len(latencies)
                }
        return stats
```

---

## 6. Voice Manager Plugin (Alternative Implementation)

### Voice Plugin for Coqui TTS

```python
# File: plugins/coqui_tts_plugin.py
"""
Coqui TTS Voice Plugin
Implements hot-swappable voice interface
"""

import numpy as np
import sounddevice as sd
from TTS.api import TTS
import time
from typing import Dict, Any
import logging

from core.plugin_base import BasePlugin, PluginMetadata
from core.message_bus import MessageBus, Event

logger = logging.getLogger(__name__)


class CoquiTtsPlugin(BasePlugin):
    """
    Coqui TTS plugin for voice synthesis.
    
    Subscribes to: 'voice_request'
    Publishes: 'audio_ready', 'voice_error'
    """
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="CoquiTTS",
            version="1.0.0",
            description="Voice synthesis via Coqui TTS",
            author="Raven Core Team",
            capabilities=["text_to_speech", "adhd_pacing", "emotional_tone"],
            dependencies=["TTS", "sounddevice"]
        )
    
    def initialize(self) -> bool:
        """
        Initialize Coqui TTS model.
        """
        try:
            model_name = self.config.get('model_name', 'tts_models/en/ljspeech/tacotron2-DDC')
            self.sample_rate = self.config.get('sample_rate', 22050)
            self.adhd_pacing = self.config.get('adhd_pacing', True)
            self.chunk_size = self.config.get('chunk_size', 30)  # words per chunk
            self.pause_duration = self.config.get('pause_duration', 300)  # ms
            
            # Load TTS model
            self.tts = TTS(model_name, progress_bar=False, gpu=False)
            
            logger.info(f"Coqui TTS loaded: {model_name}")
            
            # Subscribe to voice requests
            self.subscribe('voice_request', self.handle_voice_request)
            
            return True
            
        except Exception as e:
            logger.error(f"Coqui TTS initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """
        Cleanup TTS model.
        """
        if hasattr(self, 'tts'):
            del self.tts
        logger.info("Coqui TTS plugin shutdown")
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if TTS is loaded.
        """
        if hasattr(self, 'tts') and self.tts:
            return {
                'status': 'healthy',
                'message': 'Coqui TTS operational',
                'sample_rate': self.sample_rate
            }
        return {
            'status': 'unhealthy',
            'message': 'TTS not loaded'
        }
    
    def handle_voice_request(self, event: Event):
        """
        Handle incoming voice synthesis request.
        
        Event data should contain:
        - text: str
        - emotional_tone: Optional[str] ('comforting', 'excited', 'serious')
        - adhd_pacing: Optional[bool]
        """
        if not self.enabled:
            return
        
        try:
            text = event.data.get('text', '')
            emotional_tone = event.data.get('emotional_tone', 'neutral')
            use_pacing = event.data.get('adhd_pacing', self.adhd_pacing)
            
            if use_pacing:
                audio = self._synthesize_with_pacing(text, emotional_tone)
            else:
                audio = self._synthesize(text, emotional_tone)
            
            # Publish audio ready event
            self.publish('audio_ready', {
                'audio': audio,
                'sample_rate': self.sample_rate,
                'text': text,
                'request_id': event.data.get('request_id')
            }, priority=2)
            
        except Exception as e:
            logger.error(f"Voice synthesis failed: {e}")
            self.publish('voice_error', {
                'error': str(e),
                'request_id': event.data.get('request_id')
            })
    
    def _synthesize(self, text: str, emotional_tone: str) -> np.ndarray:
        """
        Synthesize speech without pacing.
        """
        # Apply emotional tone adjustments
        speed = self._get_speed_for_tone(emotional_tone)
        
        # Generate audio
        audio = self.tts.tts(text=text, speed=speed)
        
        return np.array(audio)
    
    def _synthesize_with_pacing(self, text: str, emotional_tone: str) -> np.ndarray:
        """
        Synthesize speech with ADHD-friendly pacing (chunks + pauses).
        """
        # Split text into chunks
        chunks = self._split_into_chunks(text, self.chunk_size)
        
        # Synthesize each chunk
        audio_segments = []
        pause_samples = int((self.pause_duration / 1000) * self.sample_rate)
        pause = np.zeros(pause_samples)
        
        for chunk in chunks:
            chunk_audio = self._synthesize(chunk, emotional_tone)
            audio_segments.append(chunk_audio)
            audio_segments.append(pause)
        
        # Concatenate all segments
        full_audio = np.concatenate(audio_segments)
        
        return full_audio
    
    def _split_into_chunks(self, text: str, max_words: int) -> list:
        """
        Split text into word-count chunks at sentence boundaries.
        """
        # Split by sentences first
        import re
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            words = sentence.split()
            
            if current_word_count + len(words) <= max_words:
                current_chunk.append(sentence)
                current_word_count += len(words)
            else:
                # Save current chunk
                if current_chunk:
                    chunks.append('. '.join(current_chunk) + '.')
                
                # Start new chunk
                current_chunk = [sentence]
                current_word_count = len(words)
        
        # Add final chunk
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        
        return chunks
    
    def _get_speed_for_tone(self, emotional_tone: str) -> float:
        """
        Get speech speed based on emotional tone.
        """
        tone_speeds = {
            'comforting': 0.9,    # Slower, calming
            'excited': 1.1,       # Faster, energetic
            'serious': 0.85,      # Slower, deliberate
            'neutral': 1.0        # Normal
        }
        return tone_speeds.get(emotional_tone, 1.0)
```

### Voice Coordinator (Audio Playback)

```python
# File: plugins/audio_player_plugin.py
"""
Audio Player Plugin
Handles audio playback from voice synthesis
"""

import sounddevice as sd
import numpy as np
from typing import Dict, Any
import logging

from core.plugin_base import BasePlugin, PluginMetadata
from core.message_bus import MessageBus, Event

logger = logging.getLogger(__name__)


class AudioPlayerPlugin(BasePlugin):
    """
    Audio player - plays synthesized speech.
    
    Subscribes to: 'audio_ready'
    Publishes: 'audio_playing', 'audio_complete'
    """
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="AudioPlayer",
            version="1.0.0",
            description="Audio playback system",
            author="Raven Core Team",
            capabilities=["audio_playback"]
        )
    
    def initialize(self) -> bool:
        """
        Initialize audio player.
        """
        try:
            # Get default audio device
            self.device = sd.default.device
            
            # Subscribe to audio ready events
            self.subscribe('audio_ready', self.handle_audio_ready)
            
            logger.info("Audio player initialized")
            return True
            
        except Exception as e:
            logger.error(f"Audio player initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """
        Cleanup audio player.
        """
        logger.info("Audio player shutdown")
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if audio device is available.
        """
        try:
            devices = sd.query_devices()
            return {
                'status': 'healthy',
                'message': 'Audio device available',
                'device': self.device
            }
        except:
            return {
                'status': 'unhealthy',
                'message': 'No audio device'
            }
    
    def handle_audio_ready(self, event: Event):
        """
        Audio is ready - play it.
        """
        if not self.enabled:
            return
        
        try:
            audio = event.data.get('audio')
            sample_rate = event.data.get('sample_rate', 22050)
            
            # Notify that playback is starting
            self.publish('audio_playing', {
                'request_id': event.data.get('request_id')
            })
            
            # Play audio
            sd.play(audio, samplerate=sample_rate)
            sd.wait()  # Block until playback finishes
            
            # Notify that playback is complete
            self.publish('audio_complete', {
                'request_id': event.data.get('request_id')
            })
            
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
```

---

**This is Part 2A (LLM + Voice)**. I need to continue with:
- Part 2B: Memory System Plugin
- Part 2C: Personality Core Plugin (Five Lenses)
- Part 3: Safety & Ethics Plugins
- Part 4: Self-Evolution (Sandbox, Plain Language, Raphael)
- Part 5: Complete Integration Example

Should I continue?
