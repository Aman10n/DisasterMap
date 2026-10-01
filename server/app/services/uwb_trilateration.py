"""
UWB Trilateration — Weighted least-squares position solver.
Takes range measurements from 4+ UWB anchors and computes 3D position.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
import structlog

logger = structlog.get_logger()


class UWBAnchor:
    """A single UWB anchor with known position."""

    def __init__(self, anchor_id: str, x: float, y: float, z: float):
        self.id = anchor_id
        self.position = np.array([x, y, z])
        self.last_range: Optional[float] = None
        self.last_quality: float = 1.0  # 0-1 quality factor


class UWBTrilateration:
    """
    Computes 3D position from UWB two-way time-of-flight ranges.
    Uses iterative weighted least-squares for robustness.
    """

    def __init__(self):
        self.anchors: Dict[str, UWBAnchor] = {}
        self.last_position: Optional[np.ndarray] = None
        self.position_history: List[Tuple[float, float, float]] = []

    def add_anchor(self, anchor_id: str, x: float, y: float, z: float):
        """Register a UWB anchor at a known position."""
        self.anchors[anchor_id] = UWBAnchor(anchor_id, x, y, z)
        logger.info("UWB anchor registered", anchor_id=anchor_id, position=(x, y, z))

    def update_range(self, anchor_id: str, range_m: float, quality: float = 1.0):
        """Update range measurement from an anchor."""
        if anchor_id in self.anchors:
            self.anchors[anchor_id].last_range = range_m
            self.anchors[anchor_id].last_quality = quality

    def solve_position(self, max_iterations: int = 20, tolerance: float = 0.001) -> Optional[Tuple[float, float, float]]:
        """
        Solve for tag position using iterative weighted least-squares.

        Returns (x, y, z) or None if insufficient data.
        """
        # Collect anchors with valid ranges
        valid_anchors = [
            a for a in self.anchors.values()
            if a.last_range is not None and a.last_range > 0
        ]

        if len(valid_anchors) < 3:
            return None

        # Initial estimate: centroid of anchors
        if self.last_position is not None:
            pos = self.last_position.copy()
        else:
            pos = np.mean([a.position for a in valid_anchors], axis=0)

        for iteration in range(max_iterations):
            # Build Jacobian (H) and residual (r)
            H = np.zeros((len(valid_anchors), 3))
            r = np.zeros(len(valid_anchors))
            W = np.zeros((len(valid_anchors), len(valid_anchors)))

            for i, anchor in enumerate(valid_anchors):
                diff = pos - anchor.position
                dist = np.linalg.norm(diff)
                if dist < 0.01:
                    dist = 0.01  # Avoid division by zero

                H[i] = diff / dist
                r[i] = dist - anchor.last_range
                W[i, i] = anchor.last_quality  # Weight by signal quality

            # Weighted least-squares update: dx = -(H^T W H)^{-1} H^T W r
            try:
                HtWH = H.T @ W @ H
                HtWr = H.T @ W @ r
                dx = -np.linalg.solve(HtWH, HtWr)
            except np.linalg.LinAlgError:
                break

            pos += dx

            if np.linalg.norm(dx) < tolerance:
                break

        self.last_position = pos.copy()
        result = tuple(pos.tolist())
        self.position_history.append(result)

        return result

    def get_accuracy_estimate(self) -> float:
        """Estimate position accuracy from residuals (meters)."""
        valid_anchors = [
            a for a in self.anchors.values()
            if a.last_range is not None and self.last_position is not None
        ]
        if not valid_anchors:
            return float('inf')

        residuals = []
        for anchor in valid_anchors:
            predicted_range = np.linalg.norm(self.last_position - anchor.position)
            residuals.append(abs(predicted_range - anchor.last_range))

        return float(np.mean(residuals))

    def get_anchor_status(self) -> List[dict]:
        """Get summary of all anchor statuses for dashboard."""
        return [
            {
                "id": a.id,
                "position": a.position.tolist(),
                "last_range": a.last_range,
                "quality": a.last_quality,
                "responding": a.last_range is not None,
            }
            for a in self.anchors.values()
        ]
