"""
Fleet Coordinator — Voronoi frontier partitioning for multi-robot exploration.
Assigns frontier goals to robots to maximize coverage with minimal overlap.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import structlog

logger = structlog.get_logger()


class FrontierCluster:
    """A cluster of frontier cells identified by connected-component analysis."""

    def __init__(self, cluster_id: int, cells: List[Tuple[float, float]]):
        self.id = cluster_id
        self.cells = cells
        self.centroid = np.mean(cells, axis=0) if cells else np.zeros(2)
        self.size = len(cells)
        self.assigned_robot: Optional[str] = None
        self.utility: float = 0.0


class FleetCoordinator:
    """
    Coordinates multiple robots for efficient exploration coverage.
    Uses Voronoi-based frontier partitioning.
    """

    def __init__(self):
        self.robot_positions: Dict[str, np.ndarray] = {}
        self.robot_batteries: Dict[str, float] = {}
        self.frontier_clusters: List[FrontierCluster] = []

    def update_robot_state(
        self, robot_id: str, x: float, y: float, battery_percent: float
    ):
        """Update known robot position and battery."""
        self.robot_positions[robot_id] = np.array([x, y])
        self.robot_batteries[robot_id] = battery_percent

    def update_frontiers(self, frontier_cells: List[Tuple[float, float]]):
        """
        Update the global frontier set and cluster them.
        Uses simple distance-based clustering (connected component on grid).
        """
        if not frontier_cells:
            self.frontier_clusters = []
            return

        cells = np.array(frontier_cells)
        visited = set()
        clusters = []
        cluster_id = 0

        for i in range(len(cells)):
            if i in visited:
                continue

            # BFS flood fill
            queue = [i]
            component = []
            while queue:
                idx = queue.pop(0)
                if idx in visited:
                    continue
                visited.add(idx)
                component.append(tuple(cells[idx]))

                # Find neighbors within 0.2m
                for j in range(len(cells)):
                    if j not in visited:
                        dist = np.linalg.norm(cells[idx] - cells[j])
                        if dist < 0.3:  # ~6 cells at 5cm resolution
                            queue.append(j)

            if len(component) >= 3:  # Minimum cluster size
                clusters.append(FrontierCluster(cluster_id, component))
                cluster_id += 1

        self.frontier_clusters = clusters
        logger.info("Frontiers clustered", count=len(clusters))

    def assign_frontiers(
        self,
        hazard_positions: List[Tuple[float, float]] = None,
        w_distance: float = 1.0,
        w_size: float = 0.5,
        w_hazard: float = 0.3,
    ) -> Dict[str, Optional[Tuple[float, float]]]:
        """
        Assign frontier goals to robots using Voronoi partitioning + utility scoring.

        Returns: {robot_id: (goal_x, goal_y) or None}
        """
        if not self.robot_positions or not self.frontier_clusters:
            return {rid: None for rid in self.robot_positions}

        hazard_positions = hazard_positions or []
        assignments: Dict[str, Optional[Tuple[float, float]]] = {}
        assigned_clusters = set()

        # Sort robots by battery (highest first — they get primary picks)
        sorted_robots = sorted(
            self.robot_positions.keys(),
            key=lambda r: self.robot_batteries.get(r, 100.0),
            reverse=True,
        )

        for robot_id in sorted_robots:
            robot_pos = self.robot_positions[robot_id]
            battery = self.robot_batteries.get(robot_id, 100.0)

            if battery < 10.0:
                assignments[robot_id] = None  # Too low, should return to base
                continue

            best_cluster = None
            best_score = -float('inf')

            for cluster in self.frontier_clusters:
                if cluster.id in assigned_clusters:
                    continue

                # Distance cost (inverse)
                dist = np.linalg.norm(robot_pos - cluster.centroid)
                dist_score = w_distance * (1.0 / max(dist, 0.5))

                # Size utility
                size_score = w_size * np.log1p(cluster.size)

                # Hazard proximity penalty
                hazard_penalty = 0.0
                for hx, hy in hazard_positions:
                    h_dist = np.linalg.norm(cluster.centroid - np.array([hx, hy]))
                    if h_dist < 3.0:
                        hazard_penalty += w_hazard * (3.0 - h_dist) / 3.0

                utility = dist_score + size_score - hazard_penalty
                cluster.utility = utility

                if utility > best_score:
                    best_score = utility
                    best_cluster = cluster

            if best_cluster is not None:
                best_cluster.assigned_robot = robot_id
                assigned_clusters.add(best_cluster.id)
                goal = tuple(best_cluster.centroid.tolist())
                assignments[robot_id] = goal
                logger.info(
                    "Frontier assigned",
                    robot=robot_id,
                    goal=goal,
                    utility=round(best_score, 3),
                    cluster_size=best_cluster.size,
                )
            else:
                assignments[robot_id] = None

        return assignments

    def compute_relay_position(
        self,
        explorer_pos: Tuple[float, float],
        gateway_pos: Tuple[float, float],
    ) -> Tuple[float, float]:
        """
        Compute optimal relay robot position to maximize signal to both
        the gateway and the exploration robot.
        Simple midpoint heuristic (in production: gradient ascent on RSSI field).
        """
        ex = np.array(explorer_pos)
        gw = np.array(gateway_pos)
        midpoint = (ex + gw) / 2.0
        return tuple(midpoint.tolist())

    def get_fleet_summary(self) -> dict:
        """Get fleet coordination summary for dashboard."""
        return {
            "robot_count": len(self.robot_positions),
            "frontier_cluster_count": len(self.frontier_clusters),
            "assignments": {
                cluster.assigned_robot: {
                    "goal": cluster.centroid.tolist(),
                    "utility": round(cluster.utility, 3),
                    "cluster_size": cluster.size,
                }
                for cluster in self.frontier_clusters
                if cluster.assigned_robot
            },
            "unassigned_frontiers": sum(
                1 for c in self.frontier_clusters if c.assigned_robot is None
            ),
        }
