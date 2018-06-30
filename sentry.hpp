#pragma once

#include <boost/asio.hpp>

#include <opencv2/core.hpp>

#include <cstddef>
#include <optional>
#include <string>

#include "pair.hpp"


class Sentry {
public:
    Sentry(std::string tty, std::uint32_t baud_rate=115200, pair rate={5000, 4000}, pair acc={1000, 1000}, std::uint32_t feed_rate=9000);
    ~Sentry();

    bool failed = true;

    void jog(const pair_base<float>& shift);

    std::size_t send(const std::string& cmd);
    std::optional<std::string> recv_all();

    bool recv();
    bool complete();

    void set_rate(const pair& rate);
    void set_acc(const pair& acc);

private:
    static const std::string hello;
    static const std::string ok;

    std::string tty;
    std::uint32_t baud_rate;

    boost::asio::io_service io;
    boost::asio::serial_port serial;

    pair rate, acc;
    std::uint32_t feed_rate;

    pair_base<float> position;
};