from conan import ConanFile
from conan.tools.files import copy


class RehearsalPolicy(ConanFile):
    name = "zeropath-rehearsal-policy"
    version = "1.0.0"
    package_type = "header-library"
    license = "MIT"
    exports_sources = "include/*"

    def requirements(self):
        self.requires("fmt/11.0.2", transitive_headers=True)

    def package(self):
        copy(self, "*.hpp", self.source_folder, self.package_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
