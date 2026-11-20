#pragma once
#include <fmt/format.h>
#include <string>

inline std::string rehearsal_policy(const std::string& name) {
    return fmt::format("policy:{}", name);
}
