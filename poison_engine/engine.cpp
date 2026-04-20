#include <pybind11/pybind11.h>
#include <string>
#include <random>

namespace py = pybind11;

std::string poison_text(const std::string& input, double probability = 0.3) {
    std::string result;
    result.reserve(input.size() * 2); // Over-allocate to handle multi-byte utf-8 chars
    
    thread_local std::mt19937 gen(std::random_device{}());
    std::uniform_real_distribution<> dis(0.0, 1.0);

    for (char c : input) {
        bool replaced = false;
        if (dis(gen) < probability) {
            switch (c) {
                // Lowercase substitutions
                case 'a': result += "\xd0\xb0"; replaced = true; break;
                case 'e': result += "\xd0\xb5"; replaced = true; break;
                case 'o': result += "\xd0\xbe"; replaced = true; break;
                case 'p': result += "\xd1\x80"; replaced = true; break;
                case 'c': result += "\xd1\x81"; replaced = true; break;
                case 'x': result += "\xd1\x85"; replaced = true; break;
                case 'y': result += "\xd1\x83"; replaced = true; break;
                
                // Uppercase substitutions
                case 'A': result += "\xd0\x90"; replaced = true; break;
                case 'E': result += "\xd0\x95"; replaced = true; break;
                case 'O': result += "\xd0\x9e"; replaced = true; break;
                case 'P': result += "\xd0\xa0"; replaced = true; break;
                case 'C': result += "\xd0\xa1"; replaced = true; break;
                case 'X': result += "\xd0\xa5"; replaced = true; break;
                case 'Y': result += "\xd0\xa3"; replaced = true; break;
                
                default: break;
            }
        }
        if (!replaced) {
            result += c;
        }
    }
    return result;
}

PYBIND11_MODULE(poison_engine, m) {
    m.doc() = "High-performance homoglyph substitution engine";
    m.def("poison_text", &poison_text, "Substitutes latin characters with visually identical cyrillic homoglyphs based on probability.", py::arg("input"), py::arg("probability") = 0.3);
}
