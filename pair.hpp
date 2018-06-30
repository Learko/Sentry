#pragma once

#include <cstdint>


template <class T>
struct pair_base {
    T x, y;

    pair_base() = default;
    pair_base(const pair_base<T>&) = default;
    pair_base<T>& operator=(const pair_base<T>&) = default;
    pair_base(pair_base<T>&&) = default;
    pair_base<T>& operator=(pair_base<T>&&) = default;

    pair_base<T>& operator+=(const pair_base& rhs) {
        x += rhs.x;
        y += rhs.y;

        return *this;
    }
    
    pair_base<T> operator+(const pair_base<T>& other) const {
        return { x + other.x, y + other.y };
    }
};

using pair = pair_base<std::uint32_t>;