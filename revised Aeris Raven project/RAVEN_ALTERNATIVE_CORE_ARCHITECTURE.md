# RAVEN/AERIS - Alternative Core Systems Architecture
## Complete Implementation for Paul's Review

**Prepared for:** Casey Monroe  
**Developer:** Paul Willis  
**Alternative Architecture by:** Claude (Anthropic)  
**Date:** October 25, 2025  

---

## EXECUTIVE SUMMARY

This document provides an **alternative implementation approach** for Raven's core systems. It's designed to help Paul see different architectural patterns and get unstuck on:

1. **Hot-swappable LLM system** (plug-and-play model switching)
2. **Hot-swappable Voice system** (plug-and-play TTS switching)
3. **Integration architecture** (how everything connects)
4. **Self-building capability** (sandbox + plain language explanations)
5. **Container system** (modular, isolated, swappable components)

**Key Differences from Paul's Current Approach:**
- Event-driven architecture (vs. linear processing)
- Plugin system with dynamic loading (vs. static imports)
- Unified message bus (vs. direct function calls)
- Declarative configuration (vs. imperative code)

---

## TABLE OF CONTENTS

### PART 1: FOUNDATIONAL ARCHITECTURE
1. System Overview & Core Principles
2. The Message Bus (Central Nervous System)
3. Plugin Architecture (Hot-Swappable Everything)
4. Configuration System (YAML-Based)

### PART 2: CORE COMPONENTS
5. LLM Manager (Alternative Implementation)
6. Voice Manager (Alternative Implementation)
7. Memory System (Alternative Implementation)
8. Personality Core (Five Lenses Integration)

### PART 3: SAFETY & ETHICS
9. Five Lenses Processor
10. Ethics Guard (Layer 2 Safety)
11. Consent Gate System
12. Crisis Detection

### PART 4: SELF-EVOLUTION
13. Sandbox Manager
14. Plain Language Explainer (Critical for Casey)
15. Raphael Retry Loop
16. Digital Twin (Self-Diagnostics)

### PART 5: INTEGRATION
17. MCP Integration Layer
18. Mode System (Comfort, Muse, Shadow, Intimacy, Child-Safe)
19. Complete System Integration Example
20. Deployment & Testing Strategy

---

# PART 1: FOUNDATIONAL ARCHITECTURE

## 1. System Overview & Core Principles

### Design Philosophy

**Problem Paul is facing:**
- Components are tightly coupled (changes ripple through system)
- Hard to swap LLMs/Voice engines without rewriting code
- Integration points are unclear
- Testing individual components is difficult

**This Alternative Approach:**
- **Loose Coupling:** Components communicate through message bus
- **Plugin Architecture:** Everything is a plugin (LLM, Voice, Memory, etc.)
- **Event-Driven:** Components react to events, not direct calls
- **Declarative Configuration:** Behavior defined in YAML, not hardcoded

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│              (Voice/Text/GUI - Entry Point)              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  MESSAGE BUS (Core)                      │
│         Event Router - All Communication Flows Here      │
└─────┬───────┬───────┬───────┬────────┬─────────┬────────┘
      │       │       │       │        │         │
      ▼       ▼       ▼       ▼        ▼         ▼
  ┌──────┐┌──────┐┌──────┐┌──────┐┌────────┐┌─────────┐
  │ LLM  ││Voice ││Memory││Person││ Safety ││ Sandbox │
  │Plugin││Plugin││Plugin││Plugin││ Plugin ││ Plugin  │
  └──────┘└──────┘└──────┘└──────┘└────────┘└─────────┘
      │       │       │       │        │         │
      └───────┴───────┴───────┴────────┴─────────┘
                     │
                     ▼
          ┌────────────────────┐
          │  CONFIGURATION      │
          │  (YAML Files)       │
          └────────────────────┘
```

### Core Principles

1. **Everything is a Plugin**
   - LLM engines
   - Voice engines
   - Memory systems
   - Personality modules
   - Safety systems
   - MCP tools

2. **Message Bus Central**
   - All communication goes through bus
   - Plugins subscribe to events
   - Plugins publish events
   - No direct plugin-to-plugin calls

3. **Configuration-Driven**
   - Behavior defined in YAML
   - Swap plugins by changing config
   - No code changes needed

4. **Fail-Safe Defaults**
   - If plugin fails, system continues
   - Fallback mechanisms everywhere
   - Graceful degradation

---

## 2. The Message Bus (Central Nervous System)

### Why a Message Bus?

**Problem:** Direct function calls create tight coupling
```python
# Paul's current approach (simplified)
response = llm_client.generate(prompt)
audio = voice_system.synthesize(response)
memory.store(response)
```

**Issue:** If LLM changes, code breaks. If voice fails, everything stops.

**Solution:** Message Bus decouples everything
```python
# Message bus approach
bus.publish('user_input', {'text': prompt})
# LLM plugin listens, generates, publishes 'llm_response'
# Voice plugin listens, synthesizes, publishes 'audio_ready'
# Memory plugin listens, stores, publishes 'memory_stored'
```

**Benefits:**
- Plugins don't know about each other
- Easy to add/remove plugins
- Easy to test (mock events)
- Easy to swap implementations

### Implementation

```python
# File: core/message_bus.py
"""
Central message bus for all system communication
Event-driven architecture - all plugins communicate through this
"""

from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import threading
import queue
import logging

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """
    Standard event format for all system communication
    """
    event_type: str           # 'user_input', 'llm_response', etc.
    data: Dict[str, Any]      # Event payload
    timestamp: datetime        # When event occurred
    source: str               # Which plugin published this
    priority: int = 5         # 1 (highest) to 10 (lowest)
    requires_response: bool = False  # Does publisher need response?
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class MessageBus:
    """
    Central event router for the entire system.
    All plugins communicate through this bus.
    
    Key Features:
    - Publish/Subscribe pattern
    - Priority queues
    - Thread-safe
    - Event logging for debugging
    - Synchronous and asynchronous event handling
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue = queue.PriorityQueue()
        self.event_history: List[Event] = []
        self.running = False
        self.lock = threading.Lock()
        self.worker_thread = None
        
        logger.info("MessageBus initialized")
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        
        Example:
            bus.subscribe('user_input', llm_plugin.handle_input)
        """
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            
            self.subscribers[event_type].append(callback)
            logger.info(f"Subscriber added for '{event_type}'")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Remove a subscription.
        """
        with self.lock:
            if event_type in self.subscribers:
                try:
                    self.subscribers[event_type].remove(callback)
                    logger.info(f"Subscriber removed for '{event_type}'")
                except ValueError:
                    pass
    
    def publish(self, event_type: str, data: Dict[str, Any], 
                source: str, priority: int = 5) -> None:
        """
        Publish an event to the bus.
        
        Args:
            event_type: Type of event
            data: Event payload
            source: Plugin publishing this event
            priority: 1 (urgent) to 10 (low priority)
        
        Example:
            bus.publish('llm_response', 
                       {'text': response, 'tokens': 150}, 
                       source='OllamaPlugin',
                       priority=3)
        """
        event = Event(
            event_type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source,
            priority=priority
        )
        
        # Store in history for debugging
        self.event_history.append(event)
        
        # Add to queue
        self.event_queue.put((priority, event))
        
        logger.debug(f"Event published: {event_type} from {source}")
    
    def process_event(self, event: Event):
        """
        Process a single event by notifying all subscribers.
        """
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in subscriber callback: {e}")
                    # Continue processing other subscribers
    
    def start(self):
        """
        Start processing events in background thread.
        """
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.worker_thread.start()
        logger.info("MessageBus started")
    
    def stop(self):
        """
        Stop processing events.
        """
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
        logger.info("MessageBus stopped")
    
    def _process_loop(self):
        """
        Main event processing loop (runs in background thread).
        """
        while self.running:
            try:
                # Get next event (blocks with timeout)
                priority, event = self.event_queue.get(timeout=0.1)
                self.process_event(event)
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
    
    def get_event_history(self, event_type: str = None, 
                          last_n: int = 10) -> List[Event]:
        """
        Get recent event history (for debugging/diagnostics).
        """
        if event_type:
            events = [e for e in self.event_history if e.event_type == event_type]
        else:
            events = self.event_history
        
        return events[-last_n:]
    
    def clear_history(self):
        """
        Clear event history (call periodically to prevent memory bloat).
        """
        with self.lock:
            self.event_history = self.event_history[-1000:]  # Keep last 1000
```

### Usage Example

```python
# Initialize bus
bus = MessageBus()
bus.start()

# Plugin A subscribes to user input
def handle_user_input(event: Event):
    print(f"Got input: {event.data['text']}")

bus.subscribe('user_input', handle_user_input)

# Plugin B publishes user input
bus.publish('user_input', 
           {'text': 'Hello Raven'}, 
           source='VoiceInput',
           priority=1)

# Plugin A receives the event automatically
```

---

## 3. Plugin Architecture (Hot-Swappable Everything)

### Plugin System Design

**Goal:** Swap any component without code changes

**How:**
1. All components implement standard interface
2. Plugins register themselves with system
3. Configuration file specifies which plugins to load
4. System loads plugins dynamically at runtime

### Base Plugin Interface

```python
# File: core/plugin_base.py
"""
Base plugin interface - all plugins must implement this
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from core.message_bus import MessageBus, Event


class PluginMetadata:
    """
    Metadata about a plugin
    """
    def __init__(self, 
                 name: str,
                 version: str,
                 description: str,
                 author: str,
                 capabilities: List[str],
                 dependencies: List[str] = None):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.capabilities = capabilities
        self.dependencies = dependencies or []


class BasePlugin(ABC):
    """
    Base class for all plugins.
    
    Every plugin (LLM, Voice, Memory, etc.) inherits from this.
    """
    
    def __init__(self, bus: MessageBus, config: Dict[str, Any]):
        self.bus = bus
        self.config = config
        self.enabled = True
        self.metadata = self.get_metadata()
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Return plugin metadata (name, version, capabilities, etc.)
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        Load models, connect to services, etc.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Cleanup and shutdown the plugin.
        Release resources, save state, etc.
        
        Returns:
            True if shutdown successful, False otherwise
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Check plugin health status.
        
        Returns:
            Dict with 'status', 'message', and other health metrics
        """
        pass
    
    def enable(self):
        """Enable this plugin"""
        self.enabled = True
    
    def disable(self):
        """Disable this plugin"""
        self.enabled = False
    
    def publish(self, event_type: str, data: Dict[str, Any], priority: int = 5):
        """
        Convenience method to publish events.
        """
        self.bus.publish(event_type, data, source=self.metadata.name, priority=priority)
    
    def subscribe(self, event_type: str, callback):
        """
        Convenience method to subscribe to events.
        """
        self.bus.subscribe(event_type, callback)
```

### Plugin Manager

```python
# File: core/plugin_manager.py
"""
Plugin manager - loads, manages, and coordinates all plugins
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, List, Any
import logging

from core.plugin_base import BasePlugin
from core.message_bus import MessageBus

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages all plugins - loading, initialization, health checks.
    
    This is what makes the system hot-swappable.
    Change config → restart → different plugins loaded.
    """
    
    def __init__(self, bus: MessageBus, config: Dict[str, Any]):
        self.bus = bus
        self.config = config
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_directory = Path(config.get('plugin_directory', './plugins'))
    
    def discover_plugins(self) -> List[str]:
        """
        Scan plugin directory and find all available plugins.
        
        Returns:
            List of plugin module names
        """
        if not self.plugin_directory.exists():
            logger.warning(f"Plugin directory not found: {self.plugin_directory}")
            return []
        
        plugin_files = list(self.plugin_directory.glob('*_plugin.py'))
        plugin_names = [f.stem for f in plugin_files]
        
        logger.info(f"Discovered {len(plugin_names)} plugins: {plugin_names}")
        return plugin_names
    
    def load_plugin(self, plugin_name: str, plugin_config: Dict[str, Any]) -> bool:
        """
        Dynamically load a plugin.
        
        Args:
            plugin_name: Name of plugin module (e.g., 'ollama_plugin')
            plugin_config: Configuration for this specific plugin
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Add plugin directory to path
            sys.path.insert(0, str(self.plugin_directory))
            
            # Import the plugin module
            module = importlib.import_module(plugin_name)
            
            # Get the plugin class (should be named like OllamaPlugin)
            class_name = ''.join(word.capitalize() for word in plugin_name.split('_'))
            plugin_class = getattr(module, class_name)
            
            # Instantiate the plugin
            plugin = plugin_class(self.bus, plugin_config)
            
            # Initialize it
            if plugin.initialize():
                self.plugins[plugin.metadata.name] = plugin
                logger.info(f"Plugin loaded: {plugin.metadata.name} v{plugin.metadata.version}")
                return True
            else:
                logger.error(f"Plugin initialization failed: {plugin_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self):
        """
        Load all plugins specified in configuration.
        """
        plugins_config = self.config.get('plugins', {})
        
        for plugin_name, plugin_config in plugins_config.items():
            if plugin_config.get('enabled', True):
                self.load_plugin(plugin_name, plugin_config)
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin (cleanup and remove).
        """
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.shutdown()
            del self.plugins[plugin_name]
            logger.info(f"Plugin unloaded: {plugin_name}")
            return True
        return False
    
    def hot_swap_plugin(self, old_plugin: str, new_plugin: str, 
                       new_config: Dict[str, Any]) -> bool:
        """
        HOT-SWAP a plugin without restarting system.
        
        This is the magic that Casey needs - swap LLM/Voice without restart.
        
        Args:
            old_plugin: Name of plugin to remove
            new_plugin: Name of plugin to load
            new_config: Configuration for new plugin
        
        Returns:
            True if swap successful, False otherwise
        """
        logger.info(f"Hot-swapping: {old_plugin} → {new_plugin}")
        
        # Load new plugin FIRST (so we don't lose functionality)
        if not self.load_plugin(new_plugin, new_config):
            logger.error("Failed to load new plugin - aborting swap")
            return False
        
        # Then unload old plugin
        if old_plugin in self.plugins:
            self.unload_plugin(old_plugin)
        
        logger.info(f"Hot-swap complete: {new_plugin} now active")
        return True
    
    def get_plugin(self, plugin_name: str) -> BasePlugin:
        """
        Get a loaded plugin by name.
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """
        Get list of all loaded plugins.
        """
        return list(self.plugins.keys())
    
    def health_check_all(self) -> Dict[str, Any]:
        """
        Run health check on all plugins.
        """
        health_status = {}
        for name, plugin in self.plugins.items():
            health_status[name] = plugin.health_check()
        
        return health_status
    
    def shutdown_all(self):
        """
        Shutdown all plugins gracefully.
        """
        logger.info("Shutting down all plugins...")
        for plugin in self.plugins.values():
            plugin.shutdown()
        self.plugins.clear()
```

### Configuration System

```python
# File: config/system_config.yaml
"""
System-wide configuration.
Change this file to swap plugins - NO CODE CHANGES NEEDED.
"""

# Core system settings
system:
  name: "Raven"
  version: "0.9.1"
  log_level: "INFO"
  plugin_directory: "./plugins"

# Message bus settings
message_bus:
  max_history: 10000
  event_timeout: 30

# Plugin configurations
plugins:
  
  # LLM Plugin - SWAP THIS TO CHANGE LLM
  ollama_plugin:
    enabled: true
    model_name: "llama3.2:3b"
    base_url: "http://localhost:11434"
    temperature: 0.7
    max_tokens: 2048
    context_window: 4096
  
  # Alternative: GPT4All plugin (commented out)
  # gpt4all_plugin:
  #   enabled: false
  #   model_name: "Phi-3.5-mini-instruct_Uncensored-Q4_K_M.gguf"
  #   model_path: "C:/Users/Casey/Raven/models"
  #   n_threads: 6
  
  # Voice Plugin - SWAP THIS TO CHANGE VOICE
  coqui_tts_plugin:
    enabled: true
    model_name: "tts_models/en/ljspeech/tacotron2-DDC"
    sample_rate: 22050
    adhd_pacing: true
    chunk_size: 30
    pause_duration: 300
  
  # Alternative: Piper plugin (commented out)
  # piper_plugin:
  #   enabled: false
  #   model_name: "en_US-amy-medium"
  #   model_path: "./voice_models"
  
  # Memory Plugin
  memory_plugin:
    enabled: true
    memory_path: "./memory"
    vector_db: "chromadb"
    encryption: true
  
  # Personality Plugin (Five Lenses + Modes)
  personality_plugin:
    enabled: true
    default_mode: "comfort"
    enable_five_lenses: true
  
  # Safety Plugin (Ethics Guard, Crisis Detection)
  safety_plugin:
    enabled: true
    crisis_detection: true
    ethics_guard: true
    consent_required: true
  
  # Sandbox Plugin (Self-evolution)
  sandbox_plugin:
    enabled: true
    sandbox_path: "./sandbox"
    max_attempts: 7
    plain_language_explanations: true
```

This architecture makes swapping components trivial:

**To swap LLM:** Change `ollama_plugin` to `gpt4all_plugin` in config, restart.  
**To swap Voice:** Change `coqui_tts_plugin` to `piper_plugin` in config, restart.  
**No code changes required.**

---

## 4. Configuration Loader

```python
# File: core/config_loader.py
"""
Configuration loader - loads YAML configs and validates them
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Loads and validates system configuration from YAML files.
    """
    
    def __init__(self, config_path: str = './config/system_config.yaml'):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def save(self, config: Dict[str, Any]):
        """
        Save configuration to YAML file.
        """
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Return minimal default configuration if file not found.
        """
        return {
            'system': {
                'name': 'Raven',
                'version': '0.9.1',
                'log_level': 'INFO'
            },
            'plugins': {}
        }
    
    def get(self, key_path: str, default=None) -> Any:
        """
        Get config value using dot notation.
        
        Example:
            config.get('plugins.ollama_plugin.model_name')
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set config value using dot notation.
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
```

---

**END OF PART 1**

This establishes the foundation:
- Message Bus (central communication)
- Plugin Architecture (hot-swappable components)
- Configuration System (declarative behavior)

**Next:** Part 2 will implement the actual plugins (LLM, Voice, Memory, Personality) using this architecture.

**For Paul:** This approach gives you:
1. Easy testing (mock the bus)
2. Easy swapping (change config)
3. Clear separation of concerns
4. Resilience (plugins fail independently)

Should I continue with Part 2?
