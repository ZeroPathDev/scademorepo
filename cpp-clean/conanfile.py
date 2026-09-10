from conan import ConanFile


class PngDemo(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires("libpng/1.6.58")
        # Keep the transitive version stable as the package index changes.
        self.requires("zlib/1.3.2", override=True)

    def layout(self):
        self.folders.build = "build"
        self.folders.generators = "build/generators"
