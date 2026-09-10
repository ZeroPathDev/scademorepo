#include <iostream>
#include <png.h>

int main() {
    std::cout << "PNG inventory thumbnails use libpng "
              << png_get_libpng_ver(nullptr) << '\n';
    return 0;
}
