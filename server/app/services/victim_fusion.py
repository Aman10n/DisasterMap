"""
Victim Sensor Fusion — Kalman Filter hypothesis tracker.
Maintains pending victim hypotheses from 4 modalities.
Promotes to confirmed when 3+ modalities associate within 90s window.
"""

import numpy as np
import structlog
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict

logger = structlog.get_logger()

ASSOCIATION_DISTANCE = 2.0  # meters (Mahalanobis)
CONFIRMATION_WINDOW = 90.0  # seconds
REQUIRED_MODALITIES = 3


class VictimKalmanState:
    """Single victim hypothesis with Kalman state."""

    def __init__(self, detection_id: int, pos: np.ndarray, modality: str, confidence: float):
        self.id = detection_id
        self.position = pos.copy()  # [x, y, z]
        self.covariance = np.eye(3) * 2.0  # Initial uncertainty: 2m
        self.modalities: Dict[str, float] = {modality: confidence}
        self.first_seen = datetime.utcnow()
        self.last_seen = datetime.utcnow()
        self.detection_count = 1
        self.confirmed = False

    @property
    def modality_count(self) -> int:
        return len(self.modalities)

    @property
    def window_active(self) -> bool:
        elapsed = (datetime.utcnow() - self.first_seen).total_seconds()
        return elapsed <= CONFIRMATION_WINDOW

    @property
    def overall_confidence(self) -> float:
        if not self.modalities:
            return 0.0
        base = sum(self.modalities.values()) / len(self.modalities)
        modality_bonus = min(self.modality_count / REQUIRED_MODALITIES, 1.0) * 0.3
        return min(base + modality_bonus, 1.0)


class VictimFusionEngine:
    """
    Manages all victim hypotheses for a mission.
    Call `process_detection()` for every incoming detection from any modality.
    """

    def __init__(self):
        self.hypotheses: List[VictimKalmanState] = []
        self._next_id = 1

    def mahalanobis_distance(self, pos: np.ndarray, hypothesis: VictimKalmanState) -> float:
        """Compute Mahalanobis distance between detection and hypothesis."""
        diff = pos - hypothesis.position
        cov_inv = np.linalg.inv(hypothesis.covariance)
        return float(np.sqrt(diff.T @ cov_inv @ diff))

    def process_detection(
        self,
        pos_x: float,
        pos_y: float,
        pos_z: float,
        modality: str,
        confidence: float,
        robot_id: str = "",
    ) -> Tuple[int, bool, bool]:
        """
        Process a single detection from any modality.

        Returns:
            (hypothesis_id, is_new_hypothesis, is_newly_confirmed)
        """
        pos = np.array([pos_x, pos_y, pos_z])

        # Find closest existing hypothesis within association distance
        best_match = None
        best_distance = float('inf')

        for hyp in self.hypotheses:
            if hyp.confirmed:
                continue  # Already confirmed, skip
            dist = self.mahalanobis_distance(pos, hyp)
            if dist < ASSOCIATION_DISTANCE and dist < best_distance:
                best_match = hyp
                best_distance = dist

        if best_match is not None:
            # Associate with existing hypothesis — Kalman update
            was_confirmed = best_match.confirmed
            self._kalman_update(best_match, pos, modality, confidence)

            # Check for promotion
            newly_confirmed = (
                not was_confirmed
                and best_match.modality_count >= REQUIRED_MODALITIES
                and best_match.window_active
            )
            if newly_confirmed:
                best_match.confirmed = True
                logger.info(
                    "Victim CONFIRMED",
                    hypothesis_id=best_match.id,
                    position=best_match.position.tolist(),
                    modalities=list(best_match.modalities.keys()),
                    confidence=best_match.overall_confidence,
                )

            return best_match.id, False, newly_confirmed

        else:
            # Create new hypothesis
            hyp_id = self._next_id
            self._next_id += 1
            new_hyp = VictimKalmanState(hyp_id, pos, modality, confidence)
            self.hypotheses.append(new_hyp)

            logger.info(
                "New victim hypothesis",
                hypothesis_id=hyp_id,
                position=pos.tolist(),
                modality=modality,
            )
            return hyp_id, True, False

    def _kalman_update(
        self, hyp: VictimKalmanState, pos: np.ndarray, modality: str, confidence: float
    ):
        """Kalman filter measurement update on hypothesis position."""
        R = np.eye(3) * (1.0 / max(confidence, 0.1))  # Measurement noise inversely proportional to confidence
        K = hyp.covariance @ np.linalg.inv(hyp.covariance + R)  # Kalman gain
        innovation = pos - hyp.position

        hyp.position = hyp.position + K @ innovation
        hyp.covariance = (np.eye(3) - K) @ hyp.covariance
        hyp.modalities[modality] = max(hyp.modalities.get(modality, 0.0), confidence)
        hyp.last_seen = datetime.utcnow()
        hyp.detection_count += 1

    def get_active_hypotheses(self) -> List[dict]:
        """Get all active (non-expired) hypotheses."""
        results = []
        for hyp in self.hypotheses:
            results.append({
                "id": hyp.id,
                "position": hyp.position.tolist(),
                "modalities": hyp.modalities,
                "modality_count": hyp.modality_count,
                "confidence": hyp.overall_confidence,
                "confirmed": hyp.confirmed,
                "detection_count": hyp.detection_count,
                "first_seen": hyp.first_seen.isoformat(),
                "last_seen": hyp.last_seen.isoformat(),
            })
        return results

    def get_confirmed_victims(self) -> List[dict]:
        """Get all confirmed victim positions."""
        return [
            {
                "id": hyp.id,
                "position": hyp.position.tolist(),
                "modalities": list(hyp.modalities.keys()),
                "confidence": hyp.overall_confidence,
                "confirmed_at": hyp.last_seen.isoformat(),
            }
            for hyp in self.hypotheses
            if hyp.confirmed
        ]
