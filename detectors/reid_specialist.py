"""
ReID Specialist - Pure Logic Unit (Gold Standard)
Maintains persistent vehicle IDs across occlusion using color histograms.
Works with VehicleRegistry in integrated mode.
"""
import cv2
import numpy as np
from detectors.base_specialist import BaseSpecialist, Event

class ReIDSpecialist(BaseSpecialist):
    def __init__(self, similarity_threshold=0.85):
        """
        Vehicle Re-Identification using color histogram embeddings.
        """
        self.similarity_threshold = similarity_threshold
        self.lost_vehicles = {}  # reid_id -> {'embedding': np.array, 'last_seen': frame_id, 'bbox': []}
        self.next_reid_id = 1
        self.track_to_reid = {}  # track_id -> reid_id mapping
        
    def load_model(self):
        """No model needed - uses color histograms"""
        pass
    
    def extract_embedding(self, crop):
        """
        Extract color histogram embedding from vehicle crop.
        Returns: normalized histogram (feature vector)
        """
        if crop is None or crop.size == 0:
            return None
        
        # Convert to HSV for better color representation
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        
        # Calculate histogram (H: 180, S: 256, V: 256)
        hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        
        # Normalize
        hist_h = cv2.normalize(hist_h, hist_h).flatten()
        hist_s = cv2.normalize(hist_s, hist_s).flatten()
        
        # Concatenate
        embedding = np.concatenate([hist_h, hist_s])
        return embedding
    
    def compare_embeddings(self, emb1, emb2):
        """
        Compare two embeddings using correlation.
        Returns: similarity score (0-1)
        """
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Correlation method
        similarity = cv2.compareHist(
            emb1.astype(np.float32), 
            emb2.astype(np.float32), 
            cv2.HISTCMP_CORREL
        )
        return max(0.0, similarity)  # Clamp to [0, 1]
    
    def find_matching_reid(self, embedding, current_frame):
        """
        Find matching ReID from lost vehicles.
        Returns: reid_id or None
        """
        best_match = None
        best_score = 0.0
        
        for reid_id, data in self.lost_vehicles.items():
            # Skip very old vehicles (> 30 frames)
            if current_frame - data['last_seen'] > 30:
                continue
            
            score = self.compare_embeddings(embedding, data['embedding'])
            if score > best_score and score > self.similarity_threshold:
                best_score = score
                best_match = reid_id
        
        return best_match
    
    def process(self, frame, frame_id=0, registry=None, tracks=None):
        """
        Process frame with pre-computed tracks and registry.
        Maintains persistent IDs across occlusion.
        
        Args:
            frame: Video frame for visualization
            frame_id: Current frame number
            registry: VehicleRegistry instance (integrated mode)
            tracks: List of Track objects (integrated mode)
        
        Returns:
            List of Event objects
        """
        if frame is None:
            return []
        
        events = []
        
        # Process tracks (if provided by integrated mode)
        if tracks is None or registry is None:
            return []
        
        h_img, w_img, _ = frame.shape
        current_track_ids = set()
        
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            current_track_ids.add(track_id)
            
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            
            # Boundary checks
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_img, x2), min(h_img, y2)
            
            # Extract crop
            vehicle_crop = frame[y1:y2, x1:x2]
            embedding = self.extract_embedding(vehicle_crop)
            
            if embedding is None:
                continue
            
            # Check if this track already has a ReID
            if track_id in self.track_to_reid:
                reid_id = self.track_to_reid[track_id]
            else:
                # Try to match with lost vehicles
                reid_id = self.find_matching_reid(embedding, frame_id)
                
                if reid_id is None:
                    # New vehicle - assign new ReID
                    reid_id = self.next_reid_id
                    self.next_reid_id += 1
                else:
                    # Re-identified! Log event
                    events.append(Event(
                        event_type="VEHICLE_REIDENTIFIED",
                        timestamp=frame_id,
                        severity="INFO",
                        description=f"Vehicle ReID#{reid_id} re-identified as Track#{track_id}",
                        source="reid_specialist",
                        metadata={"reid_id": reid_id, "track_id": track_id}
                    ))
                
                self.track_to_reid[track_id] = reid_id
            
            # Update lost vehicles database
            self.lost_vehicles[reid_id] = {
                'embedding': embedding,
                'last_seen': frame_id,
                'bbox': [x1, y1, x2-x1, y2-y1]
            }
            
            # Visualize ReID
            cv2.putText(frame, f"ReID:{reid_id}", (x1, y2 + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        
        # Cleanup lost vehicles (remove very old ones)
        to_remove = [rid for rid, data in self.lost_vehicles.items() 
                     if frame_id - data['last_seen'] > 50]
        for rid in to_remove:
            del self.lost_vehicles[rid]
        
        # Remove track mappings for tracks that disappeared
        disappeared_tracks = set(self.track_to_reid.keys()) - current_track_ids
        for tid in disappeared_tracks:
            del self.track_to_reid[tid]
        
        return events
