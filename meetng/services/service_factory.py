from enum import Enum
from typing import Optional, Dict, Type
from .base_service import TranscriptionService
from .openai_service import OpenAITranscriptionService
from .assemblyai_service import AssemblyAITranscriptionService

class ServiceType(Enum):
    """Enumeration of available service types"""
    OPENAI = "openai"
    ASSEMBLYAI = "assemblyai"

class ServiceState(Enum):
    """Enumeration of possible service states"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DISABLED = "disabled"

class ServiceFactory:
    """Factory for creating and managing transcription services"""
    
    _services: Dict[ServiceType, Type[TranscriptionService]] = {
        ServiceType.OPENAI: OpenAITranscriptionService,
        ServiceType.ASSEMBLYAI: AssemblyAITranscriptionService
    }
    
    _instances: Dict[ServiceType, TranscriptionService] = {}
    
    @classmethod
    def get_service(cls, service_type: ServiceType) -> Optional[TranscriptionService]:
        """Get or create a service instance"""
        if service_type not in cls._instances:
            service_class = cls._services.get(service_type)
            if not service_class:
                raise ValueError(f"Unknown service type: {service_type}")
            cls._instances[service_type] = service_class()
            
        return cls._instances[service_type]
    
    @classmethod
    def reset_service(cls, service_type: ServiceType) -> None:
        """Reset a service instance"""
        if service_type in cls._instances:
            del cls._instances[service_type]
