from conan import ConanFile


class PngDemo(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires("libpng/1.6.50")
        # Override the transitive version without adding a direct zlib dependency.
        self.requires("zlib/1.2.11", override=True)

    def layout(self):
        self.folders.build = "build"
        self.folders.generators = "build/generators"
