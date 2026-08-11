"""Detects whether a box has fallen off the target.

This package provides `BaseDropDetector` and its subclasses, `BoxFallOffCarrierDetector` and
`DroppedBodyDuringSimulationDetector`, which determine whether a body has fallen off the target based on
the position of its center of mass and its oriented bounding box size, either from a single snapshot or
from a recorded pose history over the course of a simulation run.
"""
