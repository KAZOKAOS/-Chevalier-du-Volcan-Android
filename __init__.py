# Recipe locale : construit Pygame 2.6.1 depuis les sources pour Android.
# Nécessaire car certaines recettes intégrées utilisent une ancienne version.
from pythonforandroid.recipes.pygame import Pygame2Recipe

class Pygame261Recipe(Pygame2Recipe):
    version = "2.6.1"
    url = "https://github.com/pygame/pygame/archive/{version}.tar.gz"
    hostpython_prerequisites = ["setuptools", "cython>=3.1"]

recipe = Pygame261Recipe()
