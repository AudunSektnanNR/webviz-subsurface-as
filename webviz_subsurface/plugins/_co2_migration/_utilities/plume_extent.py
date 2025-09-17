from typing import Iterable, List

import geojson
import numpy as np
import scipy.ndimage
import xtgeo

MISSING_DEPENDENCIES = False
try:
    import shapely.geometry
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
    Find contours using boundary detection and connected component analysis.
    """
    from scipy import ndimage
    
    # Create binary mask
    binary_mask = z_values >= 0.5
    true_count = np.sum(binary_mask)
    
    if true_count == 0 or true_count == binary_mask.size:
        return []
    
    # Find boundary using morphological operations
    # Erode the mask and XOR with original to get the boundary
    eroded = ndimage.binary_erosion(binary_mask, structure=np.ones((3, 3)))
    boundary = binary_mask & ~eroded
    
    # Label connected components of the boundary
    labeled_boundary, num_components = ndimage.label(boundary)
    
    result_contours = []
    
    for label_id in range(1, num_components + 1):
        # Get coordinates for this boundary component
        boundary_coords = np.where(labeled_boundary == label_id)
        i_coords = boundary_coords[0]
        j_coords = boundary_coords[1]
        
        if len(i_coords) < 3:  # Skip very small contours
            continue
        
        # Convert to real-world coordinates
        contour_points = []
        for i, j in zip(i_coords, j_coords):
            # Ensure we're within bounds
            i = max(0, min(i, x_mesh.shape[0] - 1))
            j = max(0, min(j, x_mesh.shape[1] - 1))
            
            x = x_mesh[i, j]
            y = y_mesh[i, j]
            contour_points.append([x, y])
        
        contour_points = np.array(contour_points)
        
        # Order points by angle from centroid
        center_x = np.mean(contour_points[:, 0])
        center_y = np.mean(contour_points[:, 1])
        
        angles = np.arctan2(contour_points[:, 1] - center_y, contour_points[:, 0] - center_x)
        sort_indices = np.argsort(angles)
        
        ordered_contour = contour_points[sort_indices]
        
        # Close the contour
        if len(ordered_contour) > 0:
            ordered_contour = np.vstack([ordered_contour, ordered_contour[0]])
            result_contours.append(ordered_contour)
    
    return result_contours


def _trace_contour_boundary(i_coords: np.ndarray, j_coords: np.ndarray, 
                           x_mesh: np.ndarray, y_mesh: np.ndarray) -> np.ndarray:
    """
    Trace a contour boundary from pixel coordinates, creating an ordered path.
    """
    if len(i_coords) == 0:
        return np.array([])
    
    # Convert to real-world coordinates
    points = []
    for i, j in zip(i_coords, j_coords):
        # Ensure indices are within bounds
        i_safe = max(0, min(i, x_mesh.shape[0] - 1))
        j_safe = max(0, min(j, x_mesh.shape[1] - 1))
        
        x = x_mesh[i_safe, j_safe] if x_mesh.shape[1] > j_safe else x_mesh[i_safe, 0]
        y = y_mesh[i_safe, j_safe] if y_mesh.shape[0] > i_safe else y_mesh[0, j_safe]
        points.append([x, y])
    
    points = np.array(points)
    
    if len(points) < 3:
        return points
    
    # Simple ordering: start from leftmost point and trace nearest neighbors
    ordered_points = []
    remaining_indices = list(range(len(points)))
    
    # Start with leftmost point
    start_idx = np.argmin(points[:, 0])
    current_idx = start_idx
    ordered_points.append(points[current_idx])
    remaining_indices.remove(current_idx)
    
    # Trace the contour by always going to the nearest remaining point
    while remaining_indices:
        current_point = ordered_points[-1]
        distances = [np.linalg.norm(points[idx] - current_point) for idx in remaining_indices]
        nearest_idx = remaining_indices[np.argmin(distances)]
        
        ordered_points.append(points[nearest_idx])
        remaining_indices.remove(nearest_idx)
        
        # Prevent infinite loops
        if len(ordered_points) > len(points):
            break
    
    # Close the contour
    if len(ordered_points) > 2:
        ordered_points.append(ordered_points[0])
    
    return np.array(ordered_points)


def _simplify(poly: np.ndarray, simplify_dist: float) -> List[List[float]]:
    simplified = shapely.geometry.LineString(poly).simplify(simplify_dist)
    return np.array(simplified.coords).tolist()  # type: ignore
