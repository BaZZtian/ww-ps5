// Inspect and bind a private module without executing any of its game functions.
#include "bind.h"
#include "recomp_table.h"
#include <iostream>
static void placeholder() {}
void* wwhd_host_symbol(const char*) { return reinterpret_cast<void*>(placeholder); }
extern "C" {
const RecompEntry* g_recomp_funcs;
unsigned g_recomp_func_count;
const RecompImport* g_recomp_imports;
unsigned g_recomp_import_count;
uint32_t g_recomp_entry_point;
}
int main(int argc, char** argv) {
    if (argc < 2 || argc > 3) return 2;
    std::string error;
    bool loaded = wwhd_load_game_module(argv[1], error);
    if (argc == 3) {
        if (loaded || error.find("different app version") == std::string::npos) return 1;
        std::cout << "Incompatible module rejected: " << error << '\n';
        return 0;
    }
    if (!loaded) { std::cerr << error << '\n'; return 1; }
    std::cout << "Bound actual module without running game code: " << g_recomp_func_count
              << " functions, " << g_recomp_import_count << " imports\n";
}
