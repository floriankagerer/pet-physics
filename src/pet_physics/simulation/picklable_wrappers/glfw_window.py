"""Picklable wrapper for a GLFW window used in MuJoCo simulation visualization."""

import glfw


class GLFWWindow:
    """Wrapper to make a GLFW window picklable."""

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        title: str = "Paletris - MuJoCo Viewer",
        monitor: glfw._GLFWmonitor | None = None,
        share: glfw._GLFWwindow | None = None,
    ):
        """The constructor.

        Args:
            width: The width of the glfw window.
            height: The height of the glfw window.
            title: The title of the window.
            monitor: Defines how the window is opened. If `None`, the window will be created in windowed mode. If this
                argument is not `None`, the window will be created in full screen mode on the specified monitor.
            share: Defines whether the context of the newly created window will share resources (like textures and
                buffers) with the specified window. This is useful for sharing OpenGL resources between context. If
                `None`, the window will not share any resources with any other window.
        """

        self._width = width
        """The width of the glfw window."""
        self._height = height
        """The height of the glfw window."""
        self._title = title
        """The title of the window."""
        self._monitor = monitor
        """Defines how the window is opened. If `None`, the window will be created in windowed mode. If this argument 
        is not `None`, the window will be created in full screen mode on the specified monitor."""
        self._share = share
        """Defines whether the context of the newly created window will share resources (like textures and buffers) 
        with the specified window. This is useful for sharing OpenGL resources between context. If `None`, the window 
        will not share any resources with any other window."""
        self._window = self._init_window()
        """The window in that the simulation is visualized."""

    @property
    def window(self) -> glfw._GLFWwindow:
        """The window in that the simulation is visualized."""
        return self._window

    def _init_window(self) -> glfw._GLFWwindow:
        """Initializes GLFW, creates the visualization window, makes OpenGL contect current and requests v-sync.

        Returns:
            The window in that the simulation is visualized.
        """
        window = glfw.create_window(self._width, self._height, self._title, self._monitor, self._share)
        glfw.make_context_current(window)
        glfw.swap_interval(1)
        return window

    def __getattr__(self, name):
        return getattr(self._window, name)

    def __setattr__(self, name, value):
        if name in ["_window", "_width", "_height", "_title", "_monitor", "_share"]:
            super().__setattr__(name, value)
        else:
            setattr(self._window, name, value)

    def __getstate__(self):
        return {
            "width": self._width,
            "height": self._height,
            "title": self._title,
            "monitor": self._monitor,
            "share": self._share,
        }

    def __setstate__(self, state):
        self.__init__(**state)

    def __del__(self, exc_type, exc_val, exc_tb):
        glfw.window_should_close(self._window)
        glfw.destroy_window(self._window)
