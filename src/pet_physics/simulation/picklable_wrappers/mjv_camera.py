"""Picklable wrapper for the MuJoCo `mujoco.MjvCamera` class."""

import mujoco


class MjvCamera:
    """Picklable wrapper around a `mujoco.MjvCamera` instance."""

    def __init__(self):
        self._mjvcamera = mujoco.MjvCamera()

    # forward all calls to the _mjvcamera instance
    def __getattr__(self, name):
        """Forwards attribute access to the wrapped `mujoco.MjvCamera` instance."""
        return getattr(self._mjvcamera, name)

    def __setattr__(self, name, value):
        """Forwards attribute assignment to the wrapped `mujoco.MjvCamera` instance."""
        if name == "_mjvcamera":
            super().__setattr__(name, value)
        else:
            setattr(self._mjvcamera, name, value)

    def __getstate__(self):
        """Returns an empty state since `mujoco.MjvCamera` is recreated on unpickling."""
        return {}

    def __setstate__(self, state):
        """Reinitializes the wrapped `mujoco.MjvCamera` instance after unpickling."""
        self.__init__()
