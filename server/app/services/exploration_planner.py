"""
Exploration Planner — Frontier detection and utility-based goal selection.
Implements the frontier-based exploration algorithm for autonomous USAR robot navigation.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
import structlog

logger = structlog.get_logger()


class FrontierCell:
    """A single frontier cell (free cell adjacent to unknown)."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.cluster_id: int = -1


class ExplorationPlanner:
    """
    Frontier-based exploration planner.
    Detects frontiers from the 2D occupancy grid, clusters them,
    and selects the highest-utility goal.
    """

    def __init__(
        self,
        w_distance: float = 1.0,
        w_size: float = 0.5,
        w_hazard: float = 0.3,
    ):
        self.w_distance = w_distance
        self.w_size = w_size
        self.w_hazard = w_hazard
        self.frontiers: List[FrontierCell] = []
        self.clusters: List[List[FrontierCell]] = []
        self.hazard_positions: List[Tuple[float, float]] = []

    def update_weights(self, w_distance: float, w_size: float, w_hazard: float):
        """Update frontier utility weights (from dashboard real-time tuning)."""
        self.w_distance = w_distance
        self.w_size = w_size
        self.w_hazard = w_hazard
        logger.info("Exploration weights updated", w_distance=w_distance, w_size=w_size, w_hazard=w_hazard)

    def detect_frontiers(
        self, occupancy_grid: np.ndarray, resolution: float = 0.05, origin_x: float = 0.0, origin_y: float = 0.0
    ) -> List[Tuple[float, float]]:
        """
        Detect frontier cells in a 2D occupancy grid.
        Free = 0, Occupied = 1, Unknown = -1

        Returns list of (x, y) frontier positions in world frame.
        """
        rows, cols = occupancy_grid.shape
        self.frontiers = []

        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if occupancy_grid[r, c] != 0:  # Not free
                    continue

                # Check if adjacent to unknown
                neighbors = [
                    occupancy_grid[r - 1, c], occupancy_grid[r + 1, c],
                    occupancy_grid[r, c - 1], occupancy_grid[r, c + 1],
                ]
                if -1 in neighbors:
                    world_x = origin_x + c * resolution
                    world_y = origin_y + r * resolution
                    self.frontiers.append(FrontierCell(world_x, world_y))

        logger.info("Frontiers detected", count=len(self.frontiers))
        return [(f.x, f.y) for f in self.frontiers]

    def cluster_frontiers(self, min_cluster_size: int = 5) -> List[List[Tuple[float, float]]]:
        """Cluster frontier cells using connected-component analysis."""
        if not self.frontiers:
            self.clusters = []
            return []

        visited = set()
        clusters = []

        for i, frontier in enumerate(self.frontiers):
            if i in visited:
                continue

            # BFS
            queue = [i]
            component = []
            while queue:
                idx = queue.pop(0)
                if idx in visited:
                    continue
                visited.add(idx)
                component.append(self.frontiers[idx])

                for j in range(len(self.frontiers)):
                    if j not in visited:
                        dx = self.frontiers[idx].x - self.frontiers[j].x
                        dy = self.frontiers[idx].y - self.frontiers[j].y
                        if (dx * dx + dy * dy) < 0.09:  # 0.3m threshold
                            queue.append(j)

            if len(component) >= min_cluster_size:
                clusters.append(component)

        self.clusters = clusters
        return [[(f.x, f.y) for f in c] for c in clusters]

    def select_goal(
        self, robot_x: float, robot_y: float
    ) -> Optional[Tuple[float, float, float]]:
        """
        Select the highest-utility frontier cluster centroid as the next goal.

        Returns (x, y, utility) or None if no frontiers.
        """
        if not self.clusters:
            return None

        best_goal = None
        best_utility = -float('inf')

        for cluster in self.clusters:
            # Centroid
            cx = np.mean([f.x for f in cluster])
            cy = np.mean([f.y for f in cluster])

            # Distance (inverse)
            dist = np.sqrt((robot_x - cx) ** 2 + (robot_y - cy) ** 2)
            dist_utility = self.w_distance * (1.0 / max(dist, 0.5))

            # Size
            size_utility = self.w_size * np.log1p(len(cluster))

            # Hazard proximity
            hazard_penalty = 0.0
            for hx, hy in self.hazard_positions:
                h_dist = np.sqrt((cx - hx) ** 2 + (cy - hy) ** 2)
                if h_dist < 5.0:
                    hazard_penalty += self.w_hazard * (5.0 - h_dist) / 5.0

            utility = dist_utility + size_utility - hazard_penalty

            if utility > best_utility:
                best_utility = utility
                best_goal = (float(cx), float(cy), float(utility))

        if best_goal:
            logger.info(
                "Exploration goal selected",
                goal=(best_goal[0], best_goal[1]),
                utility=round(best_goal[2], 3),
            )

        return best_goal
