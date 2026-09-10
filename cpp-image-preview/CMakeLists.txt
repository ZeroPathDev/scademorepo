cmake_minimum_required(VERSION 3.15)
project(image_preview LANGUAGES CXX)

find_package(PNG REQUIRED)
add_executable(image_preview main.cpp)
target_compile_features(image_preview PRIVATE cxx_std_11)
target_link_libraries(image_preview PRIVATE PNG::PNG)
