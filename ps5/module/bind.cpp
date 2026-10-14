#include "bind.h"
#include "loader.h"
#include "recomp_table.h"
#include "abi.h"
#include <cstring>
#include <stdexcept>
namespace {
game_module::Image module;
void* required(const char* name, size_t size = 1) {
    void* result = module.symbol(name, size);
    if (!result) throw std::runtime_error(std::string("Missing game symbol: ") + name);
    return result;
}
}
void* wwhd_host_symbol(const char*);
extern "C" PpcFunc wwhd_module_function(const char* name) {
    return reinterpret_cast<PpcFunc>(required(name));
}
bool wwhd_load_game_module(const char* path, std::string& error) {
    if (!module.load(path, wwhd_host_symbol, error)) return false;
    try {
        if (memcmp(required("wwhd_game_abi", sizeof(WWHD_MODULE_ABI)), WWHD_MODULE_ABI, sizeof(WWHD_MODULE_ABI)))
            throw std::runtime_error("Game package is for a different app version; rerun its matching setup");
        auto funcs = *static_cast<unsigned*>(required("g_recomp_func_count", sizeof(unsigned)));
        auto imports = *static_cast<unsigned*>(required("g_recomp_import_count", sizeof(unsigned)));
        if (!funcs || funcs > 1000000 || imports > 65536) throw std::runtime_error("Invalid game tables");
#define REQUIRE_GAME_SYMBOL(name) required(name);
#include "required.inc"
#undef REQUIRE_GAME_SYMBOL
        g_recomp_funcs = static_cast<RecompEntry*>(required("g_recomp_funcs", funcs * sizeof(RecompEntry)));
        g_recomp_imports = static_cast<RecompImport*>(required("g_recomp_imports", imports * sizeof(RecompImport)));
        g_recomp_func_count = funcs;
        g_recomp_import_count = imports;
        g_recomp_entry_point = *static_cast<uint32_t*>(required("g_recomp_entry_point", sizeof(uint32_t)));
        return true;
    } catch (const std::exception& ex) { error = ex.what(); return false; }
}
