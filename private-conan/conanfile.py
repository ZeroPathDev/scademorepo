from conan import ConanFile


class PolicyApp(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    requires = "zeropath-rehearsal-policy/1.0.0"
