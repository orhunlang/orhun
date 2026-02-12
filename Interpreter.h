#pragma once

#include "AST.h"

#include <functional>
#include <string>
#include <unordered_map>
#include <variant>
#include <vector>

// Orhun çalışma zamanı değeri.
// v0.4.1: sayı, metin ve liste desteklenir.
struct OrhunDegeri {
    using ListeTipi = std::vector<OrhunDegeri>;

    std::variant<int, std::string, ListeTipi> veri;

    OrhunDegeri() : veri(0) {}
    explicit OrhunDegeri(int v) : veri(v) {}
    explicit OrhunDegeri(std::string v) : veri(std::move(v)) {}
    explicit OrhunDegeri(const char* v) : veri(std::string(v)) {}
    explicit OrhunDegeri(ListeTipi v) : veri(std::move(v)) {}

    bool operator==(const OrhunDegeri& diger) const {
        return veri == diger.veri;
    }
};

class Interpreter {
public:
    Interpreter();

    // Program veya herhangi bir komut düğümünü çalıştırır.
    void calistir(const ASTNode* dugum);

private:
    using DegiskenTablosu = std::unordered_map<std::string, OrhunDegeri>;
    using GomuluIslev = std::function<OrhunDegeri(const std::vector<OrhunDegeri>&, std::size_t)>;

    DegiskenTablosu globalHafiza_;
    std::vector<DegiskenTablosu> yerelKapsamYigini_;

    std::unordered_map<std::string, const IslevTanimNode*> islevTablosu_;
    std::unordered_map<std::string, GomuluIslev> gomuluIslevler_;
    std::vector<std::unique_ptr<ProgramNode>> yukluModuller_;

    void gomuluIslevleriYukle();

    void calistirBlock(const BlockNode* block);
    void calistirAtama(const AtamaNode* dugum);
    void calistirYazdir(const YazdirNode* dugum);
    void calistirEger(const EgerNode* dugum);
    void calistirTekrarla(const TekrarlaNode* dugum);
    void calistirIslevTanim(const IslevTanimNode* dugum);
    void calistirDondur(const DondurNode* dugum);
    void calistirDahilEt(const DahilEtNode* dugum);
    void calistirIfadeKomut(const IfadeKomutNode* dugum);

    OrhunDegeri ifadeHesapla(const ASTNode* dugum);
    OrhunDegeri tekliIslemHesapla(const TekliIslemNode* dugum);
    OrhunDegeri ikiliIslemHesapla(const IkiliIslemNode* dugum);
    OrhunDegeri listeIslemi(const OrhunDegeri& sol,
                            const OrhunDegeri& sag,
                            const std::string& op,
                            std::size_t satir);
    OrhunDegeri sorCalistir(const SorNode* dugum);
    OrhunDegeri listeOlustur(const ListeNode* dugum);
    OrhunDegeri indeksErisim(const IndeksErisimNode* dugum);
    OrhunDegeri islevCagir(const IslevCagriNode* dugum);

    DegiskenTablosu& aktifKapsam();
    const OrhunDegeri& degiskenBul(const std::string& ad, std::size_t satir) const;

    bool dogruMu(const OrhunDegeri& deger) const;
    bool esittir(const OrhunDegeri& sol, const OrhunDegeri& sag) const;
    std::string metneCevir(const OrhunDegeri& deger) const;

    [[noreturn]] void hataFirlat(std::size_t satir, const std::string& mesaj) const;
};
