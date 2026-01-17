# Task List: Gold Standard Architecture Refactoring

## Phase 1: Foundation & Architecture
- [x] Define `BaseSpecialist` interface
- [x] Create modular directory structure
- [x] Implement basic `unified_processor.py`

## Phase 2: Individual Specialists (Standalone Mode)
- [x] Pothole Detection (Custom YOLOv8 model)
- [x] Wrong-Way Detection (Center divider logic)
- [x] Speed Detection (2-line virtual loop)
- [x] Emergency Vehicle Detection (Custom YOLOv11 model)
- [x] ReID System (Color histogram embeddings)

## Phase 3: Gold Standard Integration
- [x] Create `core/vehicle_registry.py` (Master state manager)
- [x] Refactor `unified_processor.py` (Shared detection architecture)
- [x] Adapt specialists for integrated mode
    - [x] Update `SpeedSpecialist` to use Registry
    - [x] Update `WrongWaySpecialist` to use Registry
    - [x] Update `EmergencySpecialist` to use Registry
    - [x] Update `ReIDSpecialist` to use Registry
    - [x] Keep `PotholeSpecialist` async (N-th frame)
- [x] Implement Rule Engine in Registry
- [x] Create `StandaloneAdapter` for backward compatibility
- [x] File organization (md/, tests/ folders)

## Phase 4: Testing & Optimization
- [x] Test integrated system with all 5 specialists
- [x] Verify emergency override logic
- [x] Optimize pothole detection (async processing)
- [x] Update Streamlit app for new architecture
- [x] Fine-tune Emergency Model (Threshold 0.95 + Size Filter)
- [ ] Performance benchmarking
- [ ] Create standalone test adapters for old test scripts

## Phase 5: Deployment
- [ ] Final documentation
- [ ] Docker containerization
- [ ] Production deployment guide
