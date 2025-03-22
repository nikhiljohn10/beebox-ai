import bpy
import sys
import site
import queue
import logging
import subprocess


is_background_install = False
execution_queue = queue.Queue()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


def append_modules_to_sys_path(modules_path):
    """Ensure Blender can find installed packages."""
    if modules_path not in sys.path:
        sys.path.append(modules_path)
    site.addsitedir(modules_path)


def install_package(package, modules_path):
    """Install a single package using Blender's Python."""
    try:
        logger.info(f"Installing {package}...")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "--target",
                modules_path,
                package,
            ]
        )
        logger.info(f"{package} installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package}. Error: {e}")


def install_packages(packages):
    """Install missing packages."""
    modules_path = bpy.utils.user_resource("SCRIPTS", path="modules", create=True)

    def _install_packages():
        wm = bpy.context.window_manager
        wm.progress_begin(0, len(packages))
        for i, (module_name, version) in enumerate(packages.items()):
            try:
                __import__(module_name)
            except ImportError:
                pip_spec = f"{module_name.strip()}{version.strip()}"
                install_package(pip_spec, modules_path)
            wm.progress_update(i + 1)
        wm.progress_end()

    append_modules_to_sys_path(modules_path)
    if is_background_install:
        execution_queue.put(_install_packages)
    else:
        _install_packages()


def background_install_packages():
    """Install missing packages in the background."""
    global is_background_install
    is_background_install = True

    def execute_queued_functions():
        while not execution_queue.empty():
            function = execution_queue.get()
            function()

    install_packages()
    bpy.app.timers.register(execute_queued_functions)
