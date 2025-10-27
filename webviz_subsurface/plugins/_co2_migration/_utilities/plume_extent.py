from typing import Iterable, List

import geojson
import numpy as np
import scipy.ndimage
import xtgeo

MISSING_DEPENDENCIES = False
try:
    import shapely.geometry
    from skimage import measure
except ImportError:
    MISSING_DEPENDENCIES = True


def plume_polygons(
    surfaces: List[xtgeo.RegularSurface],
    threshold: float,
    smoothing: float = 10.0,
    simplify_factor: float = 1.2,
) -> geojson.FeatureCollection:
    if MISSING_DEPENDENCIES:
        return geojson.FeatureCollection(features=[])
    plume_count = truncate_surfaces(surfaces, threshold, smoothing)
    p_levels = [0.1]
    if len(surfaces) > 2:
        p_levels.append(0.5)
    if len(surfaces) > 1:
        p_levels.append(0.9)
    levels = [lvl * len(surfaces) for lvl in p_levels]
    contours = _extract_contours(plume_count, surfaces[0], simplify_factor, levels)
    return geojson.FeatureCollection(
        features=[
            geojson.Feature(
                id=f"P{level * 100}",
                geometry=geojson.LineString(poly),
            )
            for level, polys in zip(p_levels, contours)
            for poly in polys
        ]
    )


def truncate_surfaces(
    surfaces: List[xtgeo.RegularSurface], threshold: float, smoothing: float
) -> np.ndarray:
    binary = [
        (
            np.where(np.isnan(s.values) | s.values.mask, 0.0, s.values) > threshold
        ).astype(float)
        for s in surfaces
    ]
    count = sum(binary)
    return scipy.ndimage.gaussian_filter(count, sigma=smoothing, mode="nearest")


def _extract_contours(
    surface: np.ndarray,
    ref_surface: xtgeo.RegularSurface,
    simplify_factor: float,
    levels: List[float],
) -> List:
    x = ref_surface.xori + np.arange(0, ref_surface.ncol) * ref_surface.xinc
    y = ref_surface.yori + np.arange(0, ref_surface.nrow) * ref_surface.yinc
    res = np.mean([abs(x[1] - x[0]), abs(y[1] - y[0])])
    simplify_dist = simplify_factor * res
    return _find_all_contours(x, y, surface, levels, simplify_dist)


def _find_all_contours(
    x_lin: np.ndarray,
    y_lin: np.ndarray,
    z_values: np.ndarray,
    levels: List[float],
    simplify_dist: float,
) -> List[List[List[List[float]]]]:
    x_mesh, y_mesh = np.meshgrid(x_lin, y_lin, indexing="ij")
    polys = [
        [
            _simplify(poly, simplify_dist)
            for poly in _find_contours(x_mesh, y_mesh, z_values >= level)
        ]
        for level in levels
    ]
    return polys


def _find_contours(
    x_mesh: np.ndarray,
    y_mesh: np.ndarray,
    z_values: np.ndarray,
) -> Iterable[np.ndarray]:
    """
    Find contours using scikit-image instead of matplotlib.
    Returns contours as coordinate arrays similar to matplotlib's format.
    """
    # Find contours at level 0.5 (equivalent to matplotlib's behavior)
    contours = measure.find_contours(z_values.T, 0.5)
    
    # Convert pixel coordinates to real world coordinates
    result_contours = []
    for contour in contours:
        # contour is in (row, col) format, we need (x, y)
        # Also need to interpolate to get real world coordinates
        real_contour = np.zeros_like(contour)
        real_contour[:, 0] = np.interp(contour[:, 1], np.arange(x_mesh.shape[0]), x_mesh[:, 0])
        real_contour[:, 1] = np.interp(contour[:, 0], np.arange(x_mesh.shape[1]), y_mesh[0, :])
        result_contours.append(real_contour)
    
    return result_contours


def _simplify(poly: np.ndarray, simplify_dist: float) -> List[List[float]]:
    simplified = shapely.geometry.LineString(poly).simplify(simplify_dist)
    return np.array(simplified.coords).tolist()  # type: ignore
