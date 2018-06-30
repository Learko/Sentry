#include <boost/spirit/include/karma.hpp>

#include <numeric>
#include <chrono>
#include <thread>


#include "sentry.hpp"

namespace karma = boost::spirit::karma;


Sentry::Sentry(std::string tty, std::uint32_t baud_rate, pair rate, pair acc, std::uint32_t feed_rate)
    : tty(tty), baud_rate(baud_rate), io(), serial(io, tty) {
    if (serial.is_open()) {
        serial.set_option(boost::asio::serial_port_base::baud_rate(baud_rate));
        serial.set_option(boost::asio::serial_port_base::character_size( 8 ));
        serial.set_option(boost::asio::serial_port_base::flow_control(boost::asio::serial_port_base::flow_control::none));
        serial.set_option(boost::asio::serial_port_base::parity(boost::asio::serial_port_base::parity::none));
        serial.set_option(boost::asio::serial_port_base::stop_bits(boost::asio::serial_port_base::stop_bits::one));

        boost::asio::streambuf sb;
        sb.prepare(hello.size());

        boost::asio::read(serial, sb, boost::asio::transfer_at_least(hello.size()));

        // set_rate(rate);
        // set_acc(acc);

        failed = false;
    }
    else {
        failed = true;
    }
}

Sentry::~Sentry() {
    if (serial.is_open()) {
        serial.close();
    }
}


std::size_t Sentry::send(const std::string& cmd) {
    static int i = 0;
    std::cout << "Send[" << i++ << "]: " << cmd << std::endl;

    return boost::asio::write(serial, boost::asio::buffer(cmd.c_str(), cmd.length()));
}

std::optional<std::string> Sentry::recv_all() {
    boost::asio::streambuf sb;
    boost::system::error_code ec;

    boost::asio::read(serial, sb, boost::asio::transfer_all(), ec);

    if (!ec) {
        return std::string(std::istreambuf_iterator<char>(&sb), std::istreambuf_iterator<char>());
    }
    else {
        return {};
    }
}

bool Sentry::recv() {
    boost::asio::streambuf sb;
    boost::system::error_code ec;

    auto size = boost::asio::read_until(serial, sb, "\r\n");
    // char o = sb.sgetc();
    sb.consume(size);

    return true;//o == 'o'; // is part of "ok\r\n"?
}

bool Sentry::complete() {
    return recv() && recv();
}


void Sentry::jog(const pair_base<float>& shift) {    
    if (std::abs(position.y + shift.y) < 10) {
        position += shift;

        std::string cmd;
        karma::generate(
            std::back_inserter(cmd),
            "$J=G90 G21 X" << karma::float_ << " Y" << karma::float_ << " F" << karma::int_ << "\r\n",
            shift.x, shift.y, baud_rate
        );

        send(cmd);
        failed = complete();
    }
}

void Sentry::set_rate(const pair& rate) {
    std::string cmd;
    karma::generate(
        std::back_inserter(cmd),
        "$110=" << karma::int_ << "\r\n" <<
        "$111=" << karma::int_ << "\r\n",
        rate.x, rate.y
    );

    send(cmd);
    failed = complete() && complete();
}

void Sentry::set_acc(const pair& acc) {
    std::string cmd;
    karma::generate(
        std::back_inserter(cmd),
        "$120=" << karma::int_ << "\r\n" <<
        "$121=" << karma::int_ << "\r\n",
        acc.x, acc.y
    );

    send(cmd);
    failed = complete() && complete();
}


const std::string Sentry::hello = "\r\nGrbl 1.1f ['$' for help]\r\n";
const std::string Sentry::ok = "ok\r\n";