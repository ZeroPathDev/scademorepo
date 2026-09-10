from conan import ConanFile


class ImagePreview(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires("libpng/1.6.50")
        self.requires("zlib/1.2.11", override=True)

    def layout(self):
        self.folders.build = "build"
        self.folders.generators = "build/generators"
