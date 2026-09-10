cmake_minimum_required(VERSION 3.15)
project(sca_png_demo LANGUAGES CXX)

find_package(PNG REQUIRED)
add_executable(sca_png_demo main.cpp)
target_compile_features(sca_png_demo PRIVATE cxx_std_11)
target_link_libraries(sca_png_demo PRIVATE PNG::PNG)
