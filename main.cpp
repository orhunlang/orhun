#include "Interpreter.h"
#include "Lexer.h"
#include "Parser.h"

#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

int main(int argc, char* argv[]) {
    // main artık gömülü test kodu çalıştırmaz.
    // Kullanıcıdan .oh dosya yolu argüman olarak beklenir.
    if (argc < 2) {
        std::cout << "Kullanım: ./orhun <dosya_adi.oh>\n";
        return 1;
    }

    const std::string dosyaYolu = argv[1];
    if (dosyaYolu.size() < 3 || dosyaYolu.substr(dosyaYolu.size() - 3) != ".oh") {
        std::cerr << "Hata: Orhun kaynak dosyası .oh uzantılı olmalıdır.\n";
        return 1;
    }

    std::ifstream dosya(dosyaYolu, std::ios::binary);
    if (!dosya.is_open()) {
        std::cerr << "Hata: '" << dosyaYolu << "' dosyası açılamadı.\n";
        return 1;
    }

    std::ostringstream tampon;
    tampon << dosya.rdbuf();
    const std::string kaynakKod = tampon.str();

    try {
        Lexer lexer(kaynakKod);
        std::vector<Token> tokenlar = lexer.tokenize();

        Parser parser(std::move(tokenlar));
        std::unique_ptr<ProgramNode> program = parser.parse();

        Interpreter yorumlayici;
        yorumlayici.calistir(program.get());
    } catch (const std::exception& ex) {
        std::cerr << ex.what() << '\n';
        return 1;
    }

    return 0;
}
