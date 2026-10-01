"""
Map Processor — OctoMap diff application + Open3D mesh generation.
Applies binary voxel diffs to the global OctoMap and generates triangle meshes
for Three.js streaming to the dashboard.
"""

import numpy as np
import structlog
from typing import Dict, List, Tuple, Optional
import msgpack
import time

logger = structlog.get_logger()


class VoxelGrid:
    """
    In-memory voxel grid representing the OctoMap state.
    Uses a dict-based sparse representation for efficiency.
    """

    def __init__(self, resolution: float = 0.05):
        self.resolution = resolution
        self.voxels: Dict[Tuple[int, int, int], float] = {}  # (ix, iy, iz) → occupancy log-odds
        self.updated_voxels: set = set()  # Track which voxels changed since last mesh gen
        self._mesh_cache: Optional[dict] = None
        self._mesh_dirty = True

    def world_to_index(self, x: float, y: float, z: float) -> Tuple[int, int, int]:
        return (
            int(np.floor(x / self.resolution)),
            int(np.floor(y / self.resolution)),
            int(np.floor(z / self.resolution)),
        )

    def index_to_world(self, ix: int, iy: int, iz: int) -> Tuple[float, float, float]:
        return (
            (ix + 0.5) * self.resolution,
            (iy + 0.5) * self.resolution,
            (iz + 0.5) * self.resolution,
        )

    def apply_diff(self, diff_data: bytes) -> int:
        """
        Apply a binary diff message to the voxel grid.
        Format: msgpack array of [x, y, z, log_odds] tuples.
        Returns number of voxels updated.
        """
        try:
            updates = msgpack.unpackb(diff_data, raw=False)
            count = 0
            for update in updates:
                x, y, z, log_odds = update
                idx = self.world_to_index(x, y, z)
                self.voxels[idx] = log_odds
                self.updated_voxels.add(idx)
                count += 1
            self._mesh_dirty = True
            return count
        except Exception as e:
            logger.error("Failed to apply voxel diff", error=str(e))
            return 0

    def get_occupied_voxels(self, threshold: float = 0.0) -> List[Tuple[float, float, float]]:
        """Get world positions of all occupied voxels."""
        occupied = []
        for idx, log_odds in self.voxels.items():
            if log_odds > threshold:
                occupied.append(self.index_to_world(*idx))
        return occupied

    def generate_mesh(self) -> dict:
        """
        Generate a triangle mesh from occupied voxels using simple cube geometry.
        Returns mesh data in Three.js-compatible format.
        """
        if not self._mesh_dirty and self._mesh_cache is not None:
            return self._mesh_cache

        t_start = time.time()
        occupied = self.get_occupied_voxels()

        if not occupied:
            self._mesh_cache = {"vertices": [], "normals": [], "colors": [], "indices": []}
            self._mesh_dirty = False
            return self._mesh_cache

        vertices = []
        normals = []
        colors = []
        indices = []

        half = self.resolution / 2.0
        vertex_count = 0

        # Cube face templates
        cube_faces = [
            # Front  (+Z)
            ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1), (0, 0, 1)),
            # Back   (-Z)
            ((1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1), (0, 0, -1)),
            # Top    (+Y)
            ((-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1), (0, 1, 0)),
            # Bottom (-Y)
            ((-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (0, -1, 0)),
            # Right  (+X)
            ((1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1), (1, 0, 0)),
            # Left   (-X)
            ((-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, 0, 0)),
        ]

        for cx, cy, cz in occupied:
            # Color based on height (blue=low, cyan=mid, white=high)
            h_norm = min(max((cz + 1.0) / 5.0, 0.0), 1.0)
            r = 0.15 + h_norm * 0.6
            g = 0.6 + h_norm * 0.35
            b = 0.85

            for face in cube_faces:
                v1, v2, v3, v4, norm = face
                for vx, vy, vz in [v1, v2, v3, v4]:
                    vertices.extend([cx + vx * half, cy + vy * half, cz + vz * half])
                    normals.extend(norm)
                    colors.extend([r, g, b])

                # Two triangles per face
                base = vertex_count
                indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])
                vertex_count += 4

        elapsed = time.time() - t_start
        logger.info(
            "Mesh generated",
            voxel_count=len(occupied),
            vertex_count=vertex_count,
            triangle_count=len(indices) // 3,
            elapsed_ms=round(elapsed * 1000, 1),
        )

        self._mesh_cache = {
            "vertices": vertices,
            "normals": normals,
            "colors": colors,
            "indices": indices,
            "voxel_count": len(occupied),
            "resolution": self.resolution,
        }
        self._mesh_dirty = False
        self.updated_voxels.clear()
        return self._mesh_cache

    def get_floor_slice(self, z_min: float, z_max: float) -> List[Tuple[float, float, float]]:
        """Get 2D projection of occupied voxels within height range."""
        return [
            (x, y, z) for x, y, z in self.get_occupied_voxels()
            if z_min <= z <= z_max
        ]

    @property
    def stats(self) -> dict:
        total = len(self.voxels)
        occupied = sum(1 for v in self.voxels.values() if v > 0)
        return {
            "total_voxels": total,
            "occupied_voxels": occupied,
            "free_voxels": total - occupied,
            "resolution": self.resolution,
        }


# Global map processor instances (per mission)
_map_processors: Dict[int, VoxelGrid] = {}


def get_map_processor(mission_id: int, resolution: float = 0.05) -> VoxelGrid:
    """Get or create a map processor for a mission."""
    if mission_id not in _map_processors:
        _map_processors[mission_id] = VoxelGrid(resolution)
    return _map_processors[mission_id]
