#include <boost/program_options.hpp>

#include <opencv2/core.hpp>
#include <opencv2/objdetect/objdetect.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc.hpp>

#include <cstddef>
#include <iostream>
#include <limits>
#include <optional>
#include <string>
#include <vector>

#include "pair.hpp"
#include "sentry.hpp"


namespace po = boost::program_options;


struct match {
    cv::Point center;
    std::uint32_t distance = std::numeric_limits<std::uint32_t>::max();
};


int main(int argc, char *argv[]) {
    std::string tty, face_casc_path, eyes_casc_path;
    std::uint32_t id;
    std::uint32_t width, height;

    po::variables_map vm;
    po::options_description opts("Allowed options");
    opts.add_options()
        ("tty,t", po::value<std::string>(&tty)
            ->default_value("/dev/ttyACM0"), "serial port")
        ("device-id,i", po::value<std::uint32_t>(&id)
            ->default_value(0), "camera device id")
        ("width,w", po::value<std::uint32_t>(&width)
            ->default_value(640), "screen width")
        ("height,h", po::value<std::uint32_t>(&height)
            ->default_value(480), "screen height")
        ("face-cascade,fc", po::value<std::string>(&face_casc_path)
            ->default_value("haarcascades/haarcascade_frontalface_default.xml"), "path to face haarcascade file")
        ("eyes-cascade,ec", po::value<std::string>(&eyes_casc_path)
            ->default_value("haarcascades/haarcascade_eye.xml"), "path to eyes haarcascade file");

    try {
        po::store(po::parse_command_line(argc, argv, opts), vm);
        po::notify(vm);
    }
    catch (const po::error& e) {
        std::cerr << e.what() << "\n\n"
                  << opts << std::endl;

        return EXIT_FAILURE;
    }
    
    // Sentry sentry(tty);

    cv::CascadeClassifier face_cascade(face_casc_path);
    cv::CascadeClassifier eyes_cascade(eyes_casc_path);

    cv::VideoCapture capture(id);
    
    if (!capture.isOpened()) {
        std::cerr << "Can't open video capture device" << std::endl;
        return EXIT_FAILURE;
    }


    cv::namedWindow("Sentry");

    capture.set(cv::CAP_PROP_FRAME_WIDTH, width);
    capture.set(cv::CAP_PROP_FRAME_HEIGHT, height);
    cv::Mat frame;

    while (capture.read(frame)) {
        cv::Mat gray;
        cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
        cv::equalizeHist(gray, gray);

        std::vector<cv::Rect> faces;
        face_cascade.detectMultiScale(
            gray, faces, 1.3, 5, cv::CASCADE_SCALE_IMAGE, cv::Size(30, 30)
        );

        
        std::optional<match> best_match;

        for (const auto& face : faces) {
            cv::Mat roi = gray(face);

            std::vector<cv::Rect> eyes;
            eyes_cascade.detectMultiScale(
                roi, eyes, 1.1, 5, cv::CASCADE_SCALE_IMAGE, cv::Size(7, 7)
            );

            if (eyes.size() >= 2) {
                cv::Point center(face.x + face.width / 2.f, face.y + face.height / 2.f);
                std::uint32_t distance = 
                    (width  / 2 + center.x) * (width  / 2 + center.x) + 
                    (height / 2 + center.y) * (height / 2 + center.y);
                
                if (!best_match || distance < best_match.value().distance) {
                    best_match = { center, distance };
                }

                cv::rectangle(frame, face, cv::Scalar(0, 255, 0), 2);

                for (const auto& eye : eyes) {
                    cv::rectangle(
                        frame,
                        cv::Rect(face.x + eye.x, face.y + eye.y, eye.width, eye.height),
                        cv::Scalar(0, 255, 0),
                        2
                    );
                }
            }
        }
        
        if (best_match) {
            auto face = best_match.value().center;

            pair_base<int> shift = {
                static_cast<int>(width  / 2) - face.x,
                static_cast<int>(height / 2) - face.y
            };

            pair_base<float> step = {
                (std::abs(shift.x) > 20 ? (shift.x > 0 ? 1.f : -1.f) : .0f),
                (std::abs(shift.y) > 22 ? (shift.y > 0 ? 1.f : -1.f) : .0f)
            };

            if (step.x != 0 || step.y != 0) {
                std::cout << step.x << ' ' << step.y << std::endl;
                // sentry.jog(step);
            }
        }
        
        cv::imshow("Sentry", frame);
        
        if (int key = cv::waitKey(1) & 0xff; key == 27) {
            break;
        }
    }


    return EXIT_SUCCESS;
}