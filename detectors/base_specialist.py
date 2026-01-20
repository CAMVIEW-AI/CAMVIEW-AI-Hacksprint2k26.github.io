from abc import ABC, abstractmethod
from typing import List
from core.events import Event

class BaseSpecialist(ABC):
    """
    Abstract Base Class for all Specialist Wrappers.
    Ensures every external model integration follows the same contract.
    """
    
    @abstractmethod
    def load_model(self):
        """Load the external model weights and configurations."""
        pass

    @abstractmethod
    def process(self, frame, frame_id: int) -> List[Event]:
        """
        Process a single frame and return a list of standard Events.
        Must handle all external-to-internal data conversion here.
        """
        pass
