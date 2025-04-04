import abc
from dataclasses import dataclass
from typing import List, Optional

import xtgeo


@dataclass(frozen=True)
class SimulatedPolygonsAddress:
    """Specifies a unique simulated polygon set for a given ensemble realization"""

    attribute: str
    name: str
    realization: int


# Type aliases used for signature readability
PolygonsAddress = SimulatedPolygonsAddress


# Class provides data for ensemble surfaces
class EnsemblePolygonProvider(abc.ABC):
    @abc.abstractmethod
    def provider_id(self) -> str:
        """Returns string ID of the provider."""

    @abc.abstractmethod
    def attributes(self) -> List[str]:
        """Returns list of all available attributes."""

    @abc.abstractmethod
    def realizations(self) -> List[int]:
        """Returns list of all available realizations."""

    @abc.abstractmethod
    def get_polygons(
        self,
        address: PolygonsAddress,
    ) -> Optional[xtgeo.Polygons]:
        """Returns fault polygons for a given fault polygons address"""

    # @abc.abstractmethod
    # def get_surface_bounds(self, surface: EnsembleSurfaceContext) -> List[float]:
    #     """Returns the bounds for a surface [xmin,ymin, xmax,ymax]"""

    # @abc.abstractmethod
    # def get_surface_value_range(self, surface: EnsembleSurfaceContext) -> List[float]:
    #     """Returns the value range for a given surface context [zmin, zmax]"""

    # @abc.abstractmethod
    # def get_surface_as_rgba(self, surface: EnsembleSurfaceContext) -> io.BytesIO:
    #     """Returns surface as a greyscale png RGBA with encoded elevation values
    #     in a bytestream"""
