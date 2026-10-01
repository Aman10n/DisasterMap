"""
Gas Interpolation — Kriging spatial interpolation for gas concentration surfaces.
Produces smooth heatmap overlays from sparse gas sensor samples.
"""

import numpy as np
from scipy.interpolate import RBFInterpolator
from typing import List, Tuple, Dict, Optional
import structlog

logger = structlog.get_logger()


class GasInterpolator:
    """
    Spatial interpolation engine for gas readings.
    Uses RBF (Radial Basis Function) interpolation as a practical alternative
    to full kriging — similar results with lower computational cost.
    """

    def __init__(self, grid_resolution: float = 0.5):
        self.grid_resolution = grid_resolution  # meters per grid cell
        self.readings: Dict[str, List[Tuple[float, float, float]]] = {}  # gas_type → [(x, y, value), ...]

    def add_reading(self, gas_type: str, x: float, y: float, value: float):
        """Add a gas sensor reading at a spatial location."""
        if gas_type not in self.readings:
            self.readings[gas_type] = []
        self.readings[gas_type].append((x, y, value))

    def interpolate(
        self,
        gas_type: str,
        bounds: Optional[Tuple[float, float, float, float]] = None,
    ) -> Optional[dict]:
        """
        Generate interpolated gas concentration surface.

        Args:
            gas_type: Type of gas ('co', 'methane', 'nh3', 'co2')
            bounds: Optional (x_min, y_min, x_max, y_max). If None, auto-computed.

        Returns:
            Dict with grid_x, grid_y, concentrations (2D numpy arrays)
        """
        if gas_type not in self.readings or len(self.readings[gas_type]) < 3:
            return None

        points = np.array(self.readings[gas_type])
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        values = points[:, 2]

        # Compute bounds
        if bounds is None:
            margin = 2.0  # meters
            x_min, x_max = x_coords.min() - margin, x_coords.max() + margin
            y_min, y_max = y_coords.min() - margin, y_coords.max() + margin
        else:
            x_min, y_min, x_max, y_max = bounds

        # Create interpolation grid
        grid_x = np.arange(x_min, x_max, self.grid_resolution)
        grid_y = np.arange(y_min, y_max, self.grid_resolution)
        mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)
        query_points = np.column_stack([mesh_x.ravel(), mesh_y.ravel()])

        try:
            # RBF interpolation (thin-plate spline, similar to kriging)
            sample_points = np.column_stack([x_coords, y_coords])
            interpolator = RBFInterpolator(
                sample_points,
                values,
                kernel="thin_plate_spline",
                smoothing=1.0,
            )
            interpolated = interpolator(query_points)
            concentrations = interpolated.reshape(mesh_x.shape)

            # Clamp to non-negative
            concentrations = np.maximum(concentrations, 0.0)

            return {
                "grid_x": grid_x.tolist(),
                "grid_y": grid_y.tolist(),
                "concentrations": concentrations.tolist(),
                "min_value": float(concentrations.min()),
                "max_value": float(concentrations.max()),
                "sample_count": len(points),
            }

        except Exception as e:
            logger.error("Gas interpolation failed", gas_type=gas_type, error=str(e))
            return None

    def get_gradient_at(self, gas_type: str, x: float, y: float) -> Tuple[float, float]:
        """
        Compute concentration gradient at a point.
        Returns (dx, dy) gradient vector pointing toward increasing concentration.
        Used for CO2 gradient search behavior.
        """
        result = self.interpolate(gas_type)
        if result is None:
            return (0.0, 0.0)

        grid_x = np.array(result["grid_x"])
        grid_y = np.array(result["grid_y"])
        conc = np.array(result["concentrations"])

        # Find nearest grid cell
        ix = np.argmin(np.abs(grid_x - x))
        iy = np.argmin(np.abs(grid_y - y))

        # Finite difference gradient
        dx = 0.0
        dy = 0.0
        if 0 < ix < len(grid_x) - 1:
            dx = (conc[iy, ix + 1] - conc[iy, ix - 1]) / (2 * self.grid_resolution)
        if 0 < iy < len(grid_y) - 1:
            dy = (conc[iy + 1, ix] - conc[iy - 1, ix]) / (2 * self.grid_resolution)

        return (float(dx), float(dy))


# Global interpolators per mission
_gas_interpolators: Dict[int, GasInterpolator] = {}


def get_gas_interpolator(mission_id: int) -> GasInterpolator:
    if mission_id not in _gas_interpolators:
        _gas_interpolators[mission_id] = GasInterpolator()
    return _gas_interpolators[mission_id]
