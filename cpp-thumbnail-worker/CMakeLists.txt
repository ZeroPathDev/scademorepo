cmake_minimum_required(VERSION 3.15)
project(thumbnail_worker LANGUAGES CXX)

find_package(PNG REQUIRED)
add_executable(thumbnail_worker main.cpp)
target_compile_features(thumbnail_worker PRIVATE cxx_std_11)
target_link_libraries(thumbnail_worker PRIVATE PNG::PNG)
