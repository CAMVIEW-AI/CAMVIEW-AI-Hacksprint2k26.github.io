from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import time

@dataclass
class VehicleState:
    id: int
    bbox: List[int] = field(default_factory=list) # [x, y, w, h]
    centroid: Tuple[int, int] = (0, 0)
    
    # Classification
    is_emergency: bool = False
    emergency_type: str = "None" # "Ambulance", "Firetruck"
    vehicle_type: str = "Unknown"
    
    # Analytics
    speed_kmh: float = 0.0
    lane_id: str = "Unknown"
    direction: str = "Unknown"
    
    # Violations (Potential)
    is_wrong_way: bool = False
    is_overspeeding: bool = False
    
    # Cooldowns
    last_alert_time: float = 0.0
    first_seen: float = 0.0
    last_seen: float = 0.0

class VehicleRegistry:
    """
    Central Logic Brain (Master Registry)
    Manages state for all vehicles and enforces Rule Engine Logic.
    """
    def __init__(self):
        self.vehicles: Dict[int, VehicleState] = {}
        self.max_age = 2.0 # seconds to keep lost vehicles
        self.alert_cooldown = 5.0 # seconds between alerts for same vehicle

    def update_vehicle(self, track_id, bbox, vehicle_type="Unknown"):
        """Update or create vehicle state from Tracker"""
        now = time.time()
        
        if track_id not in self.vehicles:
            self.vehicles[track_id] = VehicleState(
                id=track_id, 
                first_seen=now,
                last_seen=now
            )
            
        v = self.vehicles[track_id]
        v.bbox = bbox
        v.last_seen = now
        v.vehicle_type = vehicle_type
        
        # Calculate centroid
        x, y, w, h = bbox
        v.centroid = (int(x + w/2), int(y + h/2))
        
        return v

    def mark_emergency(self, track_id, em_type):
        """Emergency Specialist Marks a vehicle"""
        if track_id in self.vehicles:
            self.vehicles[track_id].is_emergency = True
            self.vehicles[track_id].emergency_type = em_type

    def update_speed(self, track_id, speed):
        """Speed Specialist updates speed"""
        if track_id in self.vehicles:
            self.vehicles[track_id].speed_kmh = speed
            if speed > 80: # Hardcoded limit for now
                self.vehicles[track_id].is_overspeeding = True

    def update_wrong_way(self, track_id, is_wrong, lane):
        """WrongWay Specialist updates status"""
        if track_id in self.vehicles:
            self.vehicles[track_id].is_wrong_way = is_wrong
            self.vehicles[track_id].lane_id = lane

    def check_rules_and_get_events(self, track_id):
        """
        MASTER RULE ENGINE
        Returns list of Events to fire, if any.
        """
        if track_id not in self.vehicles: return []
        
        v = self.vehicles[track_id]
        events = []
        now = time.time()
        
        # Rule 0: Global Cooldown
        if now - v.last_alert_time < self.alert_cooldown:
            return []

        # Rule 1: Emergency Logic (Overrides everything)
        if v.is_emergency:
            # We ONLY fire Emergency Detected event, ignore others
            # Update alert time to enforce cooldown
            v.last_alert_time = now
            return [{
                "type": "EMERGENCY_VEHICLE",
                "severity": "CRITICAL",
                "description": f"Priority: {v.emergency_type} detected. Allowing passage.",
                "metadata": {"speed": v.speed_kmh, "wrong_way": v.is_wrong_way, "track_id": track_id}
            }]

        # Rule 2: Violations (If NOT Emergency)
        
        # Wrong Way
        if v.is_wrong_way:
            events.append({
                "type": "WRONG_WAY",
                "severity": "CRITICAL",
                "description": f"Vehicle {track_id} wrong way in {v.lane_id}",
            })
            
        # Overspeed
        if v.is_overspeeding:
             events.append({
                "type": "OVERSPEED",
                "severity": "WARNING",
                "description": f"Vehicle {track_id} Speeding: {v.speed_kmh:.1f} km/h",
            })
            
        if events:
            v.last_alert_time = now
            
        return events

    def cleanup(self):
        """Remove old vehicles"""
        now = time.time()
        expired = [vid for vid, v in self.vehicles.items() if now - v.last_seen > self.max_age]
        for vid in expired:
            del self.vehicles[vid]
