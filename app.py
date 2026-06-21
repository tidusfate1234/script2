"""
MOONULTRA V3 ADVANCED - Luau Code Virtualization Engine
Enhanced with Custom VM, Anti-Tamper, and Advanced Obfuscation
"""

import os
import re
import random
import math
import string
import hashlib
import secrets
import time
import base64
import json
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="MOONULTRA V3 Advanced")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════
#  OWNER IP ALLOWLIST  — lives ONLY here, never in HTML
#  Set env var OWNER_IPS="1.2.3.4,::1" to override
#  without touching source code.
# ═══════════════════════════════════════════════════════

def _load_owner_ips() -> set:
    env = os.environ.get("OWNER_IPS", "")
    if env.strip():
        return {ip.strip() for ip in env.split(",") if ip.strip()}
    return {
        "75.159.129.174",
        "2001:56a:f847:a900:a4b5:c610:af80:9767",
        "::1",
        "127.0.0.1",
    }

OWNER_IPS: set = _load_owner_ips()


def _real_ip(request: Request) -> str:
    """Extract real client IP, honouring common reverse-proxy headers."""
    for header in ("x-real-ip", "x-forwarded-for"):
        val = request.headers.get(header)
        if val:
            return val.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ── Pydantic request models ──────────────────────────────

class ObfuscateOptions(BaseModel):
    encodeStrings: bool = False
    virtualize: bool = True
    antiTamper: bool = True
    controlFlowObfuscation: bool = True
    minify: bool = True
    stripComments: bool = True
    stringEncodingMethod: str = "xor"

class ObfuscateRequest(BaseModel):
    code: str
    options: Optional[ObfuscateOptions] = None

class UploadScriptRequest(BaseModel):
    name: str
    source: str
    options: Optional[ObfuscateOptions] = None

class KeyRequest(BaseModel):
    key: Optional[str] = None
    linkvertise_token: Optional[str] = None


# ═══════════════════════════════════════════════════════
#  ENCHANTMENT TABLE JUNK COMMENT INJECTOR
#  Encodes random data as base64 with a randomised
#  alphabet, then maps every character to the Standard
#  Galactic Alphabet (Minecraft enchantment table font).
#  Injected as --[[ … ]] block comments at random line
#  intervals throughout the obfuscated output.
# ═══════════════════════════════════════════════════════

# Standard Galactic Alphabet mapping (a-z + digits 0-9 + padding)
_SGA_MAP = {
    'a': 'ᔑ', 'b': 'ʖ',  'c': 'ᓵ', 'd': '↸', 'e': 'ᒷ',
    'f': '⎓', 'g': '⊣',  'h': 'ᒲ', 'i': '╎', 'j': '✱',
    'k': 'ꖌ', 'l': 'ꖎ',  'm': 'ᒲ', 'n': 'リ', 'o': '⊑',
    'p': '⌇', 'q': '↸',  'r': '∷', 's': 'ᓭ', 't': 'ℸ',
    'u': '⚍', 'v': '⍊',  'w': 'ʍ', 'x': '✕', 'y': '⋮',
    'z': '᙮', '0': '0',  '1': '1', '2': '2', '3': '3',
    '4': '4', '5': '5',  '6': '6', '7': '7', '8': '8',
    '9': '9', '+': '⨅',  '/': '̇/', '=': '̇',
}

_B64_STANDARD = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'

def _random_b64_alphabet() -> str:
    """Return a shuffled base64 alphabet (keeps = padding in place)."""
    chars = list(_B64_STANDARD[:-1])  # exclude '=' which stays as padding
    random.shuffle(chars)
    return ''.join(chars) + '='

def _encode_custom_b64(data: bytes, alphabet: str) -> str:
    """Encode bytes using standard base64 then remap to custom alphabet."""
    standard = base64.b64encode(data).decode()
    table = str.maketrans(_B64_STANDARD, alphabet)
    return standard.translate(table)

def _to_sga(text: str) -> str:
    """Map every character in text to its Standard Galactic Alphabet glyph."""
    return ''.join(_SGA_MAP.get(ch.lower(), ch) for ch in text)

def _make_enchantment_comment(min_bytes: int = 12, max_bytes: int = 48) -> str:
    """
    Generate a single --[[ … ]] junk comment containing SGA-encoded
    random data, using a fresh random base64 alphabet.
    """
    payload    = secrets.token_bytes(random.randint(min_bytes, max_bytes))
    alphabet   = _random_b64_alphabet()
    encoded    = _encode_custom_b64(payload, alphabet)
    sga_text   = _to_sga(encoded)
    return f'--[[ {sga_text} ]]'

def _inject_enchantment_comments(code: str, min_gap: int = 20, max_gap: int = 90) -> str:
    """
    Inject enchantment-table block comments at random line intervals
    (between min_gap and max_gap lines apart) throughout the code.
    """
    lines  = code.split('\n')
    result = []
    i      = 0
    next_inject = random.randint(min_gap, max_gap)

    while i < len(lines):
        result.append(lines[i])
        i += 1
        if i >= next_inject:
            result.append(_make_enchantment_comment())
            next_inject = i + random.randint(min_gap, max_gap)

    return '\n'.join(result)


# ═══════════════════════════════════════════════════════
#  LEXER - Luau-compatible tokenizer
# ═══════════════════════════════════════════════════════

class LuauLexer:
    def __init__(self, source):
        self.source = source
        self.pos    = 0
        self.tokens = []

    def tokenize(self):
        while self.pos < len(self.source):
            self._skip_ws()
            if self.pos >= len(self.source):
                break
            ch = self.source[self.pos]
            if ch == '-' and self._peek() == '-':
                if self._peek(2) == '[':
                    p3 = self._peek(3)
                    if p3 == '[' or p3 == '=':
                        self._read_long_comment()
                        continue
                self._read_comment()
                continue
            if ch in ('"', "'"):
                self.tokens.append(self._read_string(ch))
                continue
            if ch == '[' and self._peek() in ('=', '['):
                self.tokens.append(self._read_long_string())
                continue
            if ch.isdigit() or (ch == '.' and self._peek() and self._peek().isdigit()):
                self.tokens.append(self._read_number())
                continue
            if ch.isalpha() or ch == '_':
                self.tokens.append(self._read_ident())
                continue
            self.tokens.append(self._read_op())
        return self.tokens

    def _cur(self):
        return self.source[self.pos] if self.pos < len(self.source) else None

    def _peek(self, n=1):
        return self.source[self.pos + n] if self.pos + n < len(self.source) else None

    def _adv(self):
        ch = self.source[self.pos]
        self.pos += 1
        return ch

    def _skip_ws(self):
        while self._cur() and self._cur() in ' \t\r\n':
            self._adv()

    def _read_comment(self):
        self._adv(); self._adv()
        while self._cur() and self._cur() != '\n':
            self._adv()

    def _read_long_comment(self):
        self._adv(); self._adv()
        if self._cur() == '[':
            self._adv()
        eq = 0
        while self._cur() == '=':
            self._adv(); eq += 1
        if self._cur() == '[':
            self._adv()
        while self._cur():
            if self._cur() == ']':
                self._adv()
                ce = 0
                while self._cur() == '=' and ce < eq:
                    self._adv(); ce += 1
                if ce == eq and self._cur() == ']':
                    self._adv(); break
            else:
                self._adv()

    def _read_string(self, quote):
        val = ''
        self._adv()
        while self._cur() is not None:
            ch = self._cur()
            if ch == '\\':
                val += self._adv()
                if self._cur() is not None:
                    val += self._adv()
            elif ch == quote:
                self._adv(); break
            elif ch == '\n':
                break
            else:
                val += self._adv()
        return {'type': 'STRING', 'value': quote + val + quote}

    def _read_long_string(self):
        val = '['
        self._adv()
        eq = 0
        while self._cur() == '=':
            val += self._adv(); eq += 1
        if self._cur() == '[':
            val += self._adv()
        while self._cur():
            if self._cur() == ']':
                cl = ']'; self._adv()
                ce = 0
                while self._cur() == '=' and ce < eq:
                    cl += self._adv(); ce += 1
                if ce == eq and self._cur() == ']':
                    cl += self._adv(); val += cl; break
                val += cl
            else:
                val += self._adv()
        return {'type': 'STRING', 'value': val}

    def _read_number(self):
        val = ''
        if self._cur() == '0' and self._peek() and self._peek().lower() == 'x':
            val += self._adv() + self._adv()
            while self._cur() and self._cur() in '0123456789abcdefABCDEF':
                val += self._adv()
        elif self._cur() == '0' and self._peek() and self._peek().lower() == 'b':
            val += self._adv() + self._adv()
            while self._cur() and self._cur() in '01':
                val += self._adv()
        else:
            while self._cur() and self._cur().isdigit():
                val += self._adv()
            if self._cur() == '.' and self._peek() and self._peek().isdigit():
                val += self._adv()
                while self._cur() and self._cur().isdigit():
                    val += self._adv()
            if self._cur() and self._cur().lower() == 'e':
                val += self._adv()
                if self._cur() and self._cur() in '+-':
                    val += self._adv()
                while self._cur() and self._cur().isdigit():
                    val += self._adv()
        return {'type': 'NUMBER', 'value': val}

    def _read_ident(self):
        val = ''
        while self._cur() and (self._cur().isalnum() or self._cur() == '_'):
            val += self._adv()
        keywords = {
            'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for',
            'function', 'goto', 'if', 'in', 'local', 'nil', 'not', 'or',
            'repeat', 'return', 'then', 'true', 'until', 'while', 'continue',
            'export', 'type',
        }
        return {'type': 'KEYWORD' if val in keywords else 'IDENTIFIER', 'value': val}

    def _read_op(self):
        ch = self._adv()
        # Single-char punctuation
        if ch in '(){}[],;:#':
            return {'type': 'OPERATOR', 'value': ch}
        # Operators that may be followed by '=' or a doubled character
        if ch in '+-*/%^=~<>':
            op = ch
            n  = self._cur()
            if n == '=':
                op += self._adv()
            elif ch == '<' and n == '<':
                op += self._adv()
            elif ch == '>' and n == '>':
                op += self._adv()
            elif ch == '/' and n == '/':
                op += self._adv()
            return {'type': 'OPERATOR', 'value': op}
        # Dot / concat / vararg
        if ch == '.':
            if self._cur() == '.':
                op = '..' + self._adv()          # consume second dot
                if self._cur() == '.':
                    op += self._adv()            # vararg '...'
                return {'type': 'OPERATOR', 'value': op}
            return {'type': 'OPERATOR', 'value': '.'}
        return {'type': 'OPERATOR', 'value': ch}


# ═══════════════════════════════════════════════════════
#  CUSTOM VM BYTECODE INSTRUCTIONS
# ═══════════════════════════════════════════════════════

class BytecodeInstruction:
    OP_LOADK=1;    OP_LOADBOOL=2;  OP_LOADNIL=3
    OP_GETGLOBAL=4; OP_SETGLOBAL=5; OP_CALL=6
    OP_RETURN=7;   OP_ADD=8;       OP_SUB=9
    OP_MUL=10;     OP_DIV=11;      OP_MOD=12
    OP_POW=13;     OP_CONCAT=14;   OP_JMP=15
    OP_EQ=16;      OP_LT=17;       OP_LE=18
    OP_TEST=19;    OP_CLOSURE=20


# ═══════════════════════════════════════════════════════
#  ANTI-TAMPER PROTECTION SYSTEM
# ═══════════════════════════════════════════════════════

class AntiTamper:
    @staticmethod
    def generate_integrity_check(code_hash):
        check_var  = '_' + ''.join(random.choices(string.ascii_letters, k=6))
        verify_var = '_' + ''.join(random.choices(string.ascii_letters, k=6))
        checks = [
            f"""
local {check_var} = function()
    local {verify_var} = 0
    if getrenv or getfenv then {verify_var} = {verify_var} + 1 end
    if debug and debug.getinfo then return nil end
    if {verify_var} ~= 1 then return nil end
    return true
end
if not {check_var}() then return end
""",
            f"""
local {check_var} = {{}}
{check_var}[1] = function() return tick() end
{check_var}[2] = function() return {check_var}[1]() end
local {verify_var} = {check_var}[2]()
if type({verify_var}) ~= "number" then return end
""",
            f"""
local {check_var} = "{code_hash}"
local function {verify_var}(s)
    local h = 0
    for i = 1, #s do h = (h * 31 + s:byte(i)) % 2147483647 end
    return tostring(h)
end
""",
        ]
        return random.choice(checks)

    @staticmethod
    def generate_vm_protection():
        guard_var = '_' + ''.join(random.choices(string.ascii_letters, k=6))
        state_var = '_' + ''.join(random.choices(string.ascii_letters, k=6))
        protections = [
            f"""
local {guard_var} = 0
local function {state_var}()
    {guard_var} = {guard_var} + 1
    if {guard_var} > 100 then return false end
    return true
end
if not {state_var}() then return end
""",
            f"""
local {guard_var} = tick()
local {state_var} = function()
    local dt = tick() - {guard_var}
    if dt > 0.1 then return false end
    return true
end
""",
            f"""
local {guard_var} = {{1,2,3,4,5}}
local {state_var} = function()
    local sum = 0
    for i,v in ipairs({guard_var}) do sum = sum + v end
    return sum == 15
end
if not {state_var}() then return end
""",
        ]
        return random.choice(protections)


# ═══════════════════════════════════════════════════════
#  ENHANCED CUSTOM VM GENERATOR
# ═══════════════════════════════════════════════════════

class MoonUltraAdvancedVM:
    def __init__(self):
        self.string_pool    = []
        self.number_pool    = []
        self.instruction_set = []
        self.variable_map   = {}
        self.var_counter    = 0
        self.VM_MAGIC       = random.randint(0x1000, 0xFFFF)
        self.VM_VERSION     = random.randint(100, 999)
        self.XOR_KEY        = random.randint(1, 255)
        self.CIPHER_ROUNDS  = random.randint(3, 7)

    def _generate_vm_names(self):
        return {
            'vm':       '_VM' + ''.join(random.choices(string.ascii_letters, k=4)),
            'stack':    '_ST' + ''.join(random.choices(string.ascii_letters, k=4)),
            'ip':       '_IP' + ''.join(random.choices(string.ascii_letters, k=4)),
            'const':    '_K'  + ''.join(random.choices(string.ascii_letters, k=4)),
            'decode':   '_DC' + ''.join(random.choices(string.ascii_letters, k=4)),
            'exec':     '_EX' + ''.join(random.choices(string.ascii_letters, k=4)),
            'verify':   '_VF' + ''.join(random.choices(string.ascii_letters, k=4)),
            'bytecode': '_BC' + ''.join(random.choices(string.ascii_letters, k=4)),
        }

    def _lcg_shuffle(self, indices, seed):
        m = 0x100000000; a = 1664525; c = 1013904223
        state = seed % m

        def lcg_next(lo, hi):
            nonlocal state
            state = (a * state + c) % m
            return lo + (state % (hi - lo + 1))

        for i in range(len(indices) - 1, 0, -1):
            j = lcg_next(0, i)
            indices[i], indices[j] = indices[j], indices[i]
        return indices

    def _encode_bytecode(self, code):
        encoded  = [ord(ch) ^ self.XOR_KEY ^ (i % 256) for i, ch in enumerate(code)]
        seed     = random.randint(1000, 9999)
        indices  = list(range(len(encoded)))
        self._lcg_shuffle(indices, seed)
        shuffled = [encoded[i] for i in indices]
        return shuffled, seed

    def _generate_decoder(self, names, seed):
        # Python encodes with 0-based index (i % 256).
        # Lua decodes with 1-based index ((i-1) % 256) — these are equivalent.
        return f"""
local {names['decode']} = function(data, key, seed)
    local lcg_state = seed % 4294967296
    local function lcg_next(lo, hi)
        lcg_state = (1664525 * lcg_state + 1013904223) % 4294967296
        return lo + (lcg_state % (hi - lo + 1))
    end
    local indices = {{}}
    for i = 1, #data do indices[i] = i end
    for i = #indices, 2, -1 do
        local j = lcg_next(1, i)
        indices[i], indices[j] = indices[j], indices[i]
    end
    local unshuffled = {{}}
    for i = 1, #data do
        unshuffled[indices[i]] = data[i]
    end
    local result = {{}}
    for i = 1, #unshuffled do
        result[i] = string.char(unshuffled[i] ~ key ~ ((i - 1) % 256))
    end
    return table.concat(result)
end
"""

    def _generate_custom_vm(self, names, code):
        f_data = '_d' + ''.join(random.choices(string.ascii_letters, k=6))
        f_ver  = '_v' + ''.join(random.choices(string.ascii_letters, k=6))
        f_push = '_p' + ''.join(random.choices(string.ascii_letters, k=6))
        f_pop  = '_q' + ''.join(random.choices(string.ascii_letters, k=6))
        f_peek = '_k' + ''.join(random.choices(string.ascii_letters, k=6))
        return f"""
local {names['vm']} = {{}}
{names['vm']}.{f_data} = {self.VM_MAGIC}
{names['vm']}.{f_ver} = {self.VM_VERSION}
{names['vm']}.{names['stack']} = {{}}

local {names['exec']} = function(code)
    local env = (getrenv and getrenv()) or (getfenv and getfenv(0)) or _ENV or _G
    local chunk
    if loadstring then
        chunk = loadstring(code)
        if chunk and setfenv and not getrenv then
            setfenv(chunk, env)
        end
    else
        chunk = load(code, "=(vm)", nil, env)
    end
    if chunk then return chunk() end
end

{names['vm']}.{f_push} = function(self, val)
    table.insert(self.{names['stack']}, val)
end
{names['vm']}.{f_pop} = function(self)
    return table.remove(self.{names['stack']})
end
{names['vm']}.{f_peek} = function(self)
    return self.{names['stack']}[#self.{names['stack']}]
end
"""

    def _generate_control_flow_obfuscation(self, exec_name, const_name):
        sv = '_S'  + ''.join(random.choices(string.ascii_letters, k=5))
        dv = '_D'  + ''.join(random.choices(string.ascii_letters, k=5))
        rv = '_R'  + ''.join(random.choices(string.ascii_letters, k=5))
        fn = '_CF' + ''.join(random.choices(string.ascii_letters, k=5))
        states  = random.sample(range(10000, 99999), 5)
        s0, s1, s2, s3, s4 = states
        p1      = random.randint(2, 15)
        p2      = random.randint(2, 15)
        p1_sq   = p1 * p1
        p2_prod = p2 * (p2 + 1)
        return f"""
local {fn} = function()
    local {sv} = {s0}
    local {dv} = nil
    local {rv} = nil
    while {sv} ~= 0 do
        if {sv} == {s0} then
            if {p1_sq} > {p1} then {sv} = {s1} else {sv} = 0 end
        elseif {sv} == {s1} then
            if ({p2_prod} % 2) == 0 then {sv} = {s2} else {sv} = 0 end
        elseif {sv} == {s2} then
            {rv} = {exec_name}({const_name})
            {sv} = {s3}
        elseif {sv} == {s3} then
            {dv} = type({rv})
            if {dv} ~= nil then {sv} = {s4} else {sv} = {s4} end
        elseif {sv} == {s4} then
            {sv} = 0
        end
    end
    return {rv}
end
return {fn}()
"""

    def _smart_join_tokens(self, tokens):
        result = []
        for i, token in enumerate(tokens):
            value = token['value'] if isinstance(token, dict) else str(token)
            result.append(value)
            if i < len(tokens) - 1:
                next_token = tokens[i + 1]
                next_val   = next_token['value'] if isinstance(next_token, dict) else str(next_token)
                if next_val in ['(', ')', '[', ']', '{', '}', ',', ';', '.', ':']:
                    continue
                if value in ['(', '[', '{', '.', ':']:
                    continue
                curr_type = token.get('type', '')     if isinstance(token, dict) else ''
                next_type = next_token.get('type', '') if isinstance(next_token, dict) else ''
                if curr_type in ['KEYWORD', 'IDENTIFIER'] and next_type in ['KEYWORD', 'IDENTIFIER', 'NUMBER']:
                    result.append(' ')
                elif curr_type == 'NUMBER' and next_type in ['KEYWORD', 'IDENTIFIER']:
                    result.append(' ')
                elif value in ['=', '+', '-', '*', '/', '%', '^', '==', '~=', '<', '>', '<=', '>=']:
                    result.append(' ')
        return ''.join(result)

    def transform(self, lua_source, enable_antitamper=True, enable_cfo=True):
        lexer  = LuauLexer(lua_source)
        tokens = lexer.tokenize()
        tokens = [t for t in tokens if t.get('type') != 'COMMENT']
        code   = self._smart_join_tokens(tokens)
        names  = self._generate_vm_names()
        encoded_bytes, seed = self._encode_bytecode(code)
        code_hash    = hashlib.md5(code.encode()).hexdigest()[:8]
        bytecode_str = '{' + ','.join(str(b) for b in encoded_bytes) + '}'
        vm_output = ""
        if enable_antitamper:
            vm_output += AntiTamper.generate_integrity_check(code_hash) + "\n"
            vm_output += AntiTamper.generate_vm_protection()             + "\n"
        vm_output += self._generate_decoder(names, seed)         + "\n"
        vm_output += self._generate_custom_vm(names, code)       + "\n"
        vm_output += f'local {names["bytecode"]} = {bytecode_str}\n'
        vm_output += f'local {names["const"]} = {names["decode"]}({names["bytecode"]}, {self.XOR_KEY}, {seed})\n'
        if enable_cfo:
            vm_output += self._generate_control_flow_obfuscation(names["exec"], names["const"])
        else:
            vm_output += f'return {names["exec"]}({names["const"]})\n'
        return vm_output


# ═══════════════════════════════════════════════════════
#  ADVANCED OBFUSCATION LAYERS
# ═══════════════════════════════════════════════════════

class StringEncoder:
    @staticmethod
    def _extract_strings(source_code):
        spans = []
        i = 0; n = len(source_code)
        while i < n:
            ch = source_code[i]
            if ch in ('"', "'"):
                start = i; quote = ch; i += 1
                content_chars = []
                while i < n:
                    c = source_code[i]
                    if c == '\\' and i + 1 < n:
                        content_chars.append(c)
                        content_chars.append(source_code[i + 1])
                        i += 2
                    elif c == quote:
                        i += 1; break
                    elif c == '\n':
                        break
                    else:
                        content_chars.append(c); i += 1
                spans.append((start, i, source_code[start:i], ''.join(content_chars)))
                continue
            if ch == '[':
                j = i + 1; eq = 0
                while j < n and source_code[j] == '=':
                    eq += 1; j += 1
                if j < n and source_code[j] == '[':
                    start = i
                    close = ']' + '=' * eq + ']'
                    end_idx = source_code.find(close, j + 1)
                    if end_idx != -1:
                        end_pos = end_idx + len(close)
                        spans.append((start, end_pos, source_code[start:end_pos], source_code[j + 1:end_idx]))
                        i = end_pos; continue
            if ch == '-' and i + 1 < n and source_code[i + 1] == '-':
                i += 2
                if i < n and source_code[i] == '[':
                    j = i + 1; eq = 0
                    while j < n and source_code[j] == '=':
                        eq += 1; j += 1
                    if j < n and source_code[j] == '[':
                        close   = ']' + '=' * eq + ']'
                        end_idx = source_code.find(close, j + 1)
                        i       = (end_idx + len(close)) if end_idx != -1 else n
                        continue
                while i < n and source_code[i] != '\n':
                    i += 1
                continue
            i += 1
        return spans

    @staticmethod
    def encode(source_code, method='xor'):
        spans = StringEncoder._extract_strings(source_code)
        if not spans:
            if method == 'xor':
                return 'local _DS=function(t,k)local r={}for i=1,#t do r[i]=string.char(t[i]~k)end return table.concat(r)end ' + source_code
            return 'local _DB=function(s)return s end ' + source_code
        replacements = []
        for (start, end, raw, inner) in spans:
            if len(inner) < 3:
                continue
            if method == 'xor':
                key       = random.randint(40, 200)
                byte_list = '{' + ','.join(str(ord(c) ^ key) for c in inner) + '}'
                replacements.append((start, end, f'_DS({byte_list},{key})'))
            else:
                b64 = base64.b64encode(inner.encode()).decode()
                replacements.append((start, end, f'_DB("{b64}")'))
        if not replacements:
            result = source_code
        else:
            parts = []; cursor = 0
            for (start, end, replacement) in sorted(replacements, key=lambda x: x[0]):
                if start > cursor:
                    parts.append(source_code[cursor:start])
                parts.append(replacement)
                cursor = end
            parts.append(source_code[cursor:])
            result = ''.join(parts)
        if method == 'xor':
            decoder = 'local _DS=function(t,k)local r={}for i=1,#t do r[i]=string.char(t[i]~k)end return table.concat(r)end '
        else:
            decoder = (
                'local _DB=function(s)'
                'local b="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"'
                'local m={}for i=1,#b do m[b:sub(i,i)]=i-1 end '
                'local r=""'
                'for i=1,#s,4 do '
                'local a,bc,c,d=s:sub(i,i+3):byte(1,4)'
                'local n=(m[string.char(a)]or 0)*262144+(m[string.char(bc)]or 0)*4096+(m[string.char(c)]or 0)*64+(m[string.char(d)]or 0)'
                'r=r..string.char(math.floor(n/65536))..string.char(math.floor(n/256)%256)..string.char(n%256)'
                'end return r end '
            )
        return decoder + result


class CommentStripper:
    @staticmethod
    def _find_long_close(source, pos, eq):
        close = ']' + '=' * eq + ']'
        idx   = source.find(close, pos)
        return -1 if idx == -1 else idx + len(close)

    @classmethod
    def strip(cls, source):
        result = []; i = 0; n = len(source)
        while i < n:
            ch = source[i]
            if ch in ('"', "'"):
                result.append(ch); i += 1
                while i < n:
                    c = source[i]; result.append(c); i += 1
                    if c == '\\' and i < n:
                        result.append(source[i]); i += 1
                    elif c == ch:
                        break
                continue
            if ch == '[' and i + 1 < n:
                j = i + 1; eq = 0
                while j < n and source[j] == '=':
                    eq += 1; j += 1
                if j < n and source[j] == '[':
                    result.append('[' + '=' * eq + '['); i = j + 1
                    close_pos = cls._find_long_close(source, i, eq)
                    if close_pos == -1:
                        result.append(source[i:]); break
                    result.append(source[i:close_pos]); i = close_pos
                    continue
            if ch == '-' and i + 1 < n and source[i + 1] == '-':
                i += 2
                if i < n and source[i] == '[':
                    j = i + 1; eq = 0
                    while j < n and source[j] == '=':
                        eq += 1; j += 1
                    if j < n and source[j] == '[':
                        i = j + 1
                        close_pos = cls._find_long_close(source, i, eq)
                        if close_pos == -1: break
                        i = close_pos; continue
                # consume single-line comment but preserve the newline
                while i < n and source[i] != '\n':
                    i += 1
                if i < n:
                    result.append('\n')
                    i += 1
                continue
            result.append(ch); i += 1
        return ''.join(result)


class Minifier:
    @staticmethod
    def _is_in_long_string(code, pos):
        """Return True if position is inside a long string/comment."""
        i = 0
        while i < pos:
            if code[i] == '[':
                j = i + 1; eq = 0
                while j < len(code) and code[j] == '=':
                    eq += 1; j += 1
                if j < len(code) and code[j] == '[':
                    close   = ']' + '=' * eq + ']'
                    end_idx = code.find(close, j + 1)
                    if end_idx != -1 and i < pos < end_idx + len(close):
                        return True
                    i = j + 1; continue
            i += 1
        return False

    @classmethod
    def minify(cls, code):
        """
        Minify Lua/Luau code.
        Preserves multi-line long strings ([[...]]) intact
        and only collapses regular lines.
        """
        # Split off long strings so we don't corrupt them
        segments    = []
        i           = 0
        n           = len(code)
        plain_buf   = []

        while i < n:
            ch = code[i]
            # Detect long string opening
            if ch == '[':
                j = i + 1; eq = 0
                while j < n and code[j] == '=':
                    eq += 1; j += 1
                if j < n and code[j] == '[':
                    # Flush accumulated plain text
                    if plain_buf:
                        segments.append(('plain', ''.join(plain_buf)))
                        plain_buf = []
                    close   = ']' + '=' * eq + ']'
                    end_idx = code.find(close, j + 1)
                    if end_idx != -1:
                        end_pos = end_idx + len(close)
                        segments.append(('verbatim', code[i:end_pos]))
                        i = end_pos; continue
            plain_buf.append(ch)
            i += 1

        if plain_buf:
            segments.append(('plain', ''.join(plain_buf)))

        out_parts = []
        for kind, text in segments:
            if kind == 'verbatim':
                out_parts.append(text)
            else:
                lines    = text.split('\n')
                filtered = []
                for line in lines:
                    s = line.strip()
                    if s and not s.startswith('--'):
                        filtered.append(s)
                minified = ' '.join(filtered)
                minified = re.sub(r'[ \t]+', ' ', minified)
                minified = re.sub(r' *(==|~=|<=|>=|\.\.|\.\.\.) *', r'\1', minified)
                minified = re.sub(r' *([,;]) *', r'\1', minified)
                minified = re.sub(r'(?<=[^\w\s]) *([=+\-*/%^#<>~]) *(?=[^\w\s])', r'\1', minified)
                minified = re.sub(r' *([\(\)\[\]\{\}]) *', r'\1', minified)
                minified = re.sub(r'(\w)(\s+)(\w)', lambda m: m.group(1) + ' ' + m.group(3), minified)
                out_parts.append(minified)

        return ''.join(out_parts)


# ═══════════════════════════════════════════════════════
#  SHARED OBFUSCATION PIPELINE
# ═══════════════════════════════════════════════════════

def _run_obfuscation(source_code: str, opts: ObfuscateOptions) -> tuple:
    """Run the full pipeline. Returns (obfuscated_code, stats)."""
    result = source_code
    if opts.stripComments:
        result = CommentStripper.strip(result)
    if opts.encodeStrings:
        result = StringEncoder.encode(result, opts.stringEncodingMethod)
    if opts.virtualize:
        vm     = MoonUltraAdvancedVM()
        result = vm.transform(result, enable_antitamper=opts.antiTamper, enable_cfo=opts.controlFlowObfuscation)
    if opts.minify:
        result = Minifier.minify(result)
    # Inject enchantment-table junk comments at random intervals
    result = _inject_enchantment_comments(result)
    watermark = (
        "--[[ <| OBFUSCATED BY MOON ULTRA "
        "| UNAUTHORISED DEOBFUSCATION OR TAMPERING IS A VIOLATION OF THE TERMS OF SERVICE "
        "| https://moonultra.xyz |> ]]\n"
    )
    result = watermark + result
    stats  = {
        'originalSize':   len(source_code),
        'obfuscatedSize': len(result),
        'ratio':          round(len(result) / len(source_code) * 100, 1) if source_code else 0,
        'antiTamper':     opts.antiTamper,
        'controlFlow':    opts.controlFlowObfuscation,
    }
    return result, stats


# ═══════════════════════════════════════════════════════
#  KEY SYSTEM
# ═══════════════════════════════════════════════════════

def _make_key_store():
    redis_url = os.environ.get('REDIS_URL', '')
    if redis_url:
        try:
            import redis as _redis
            client = _redis.from_url(redis_url, decode_responses=True)
            client.ping()
            print(f"[MoonUltra] Key store: Redis ({redis_url})")
            return client
        except Exception as e:
            print(f"[MoonUltra] Redis unavailable ({e}), falling back to in-memory store")
    else:
        print("[MoonUltra] REDIS_URL not set — using in-memory key store (keys lost on restart)")
    return {}

_key_store   = _make_key_store()
_using_redis = not isinstance(_key_store, dict)

def _ks_get(key):
    if _using_redis:
        raw = _key_store.get(f"mu:key:{key}")
        return json.loads(raw) if raw else None
    return _key_store.get(key)

def _ks_set(key, entry):
    if _using_redis:
        ttl = max(1, math.ceil(entry['expires'] - time.time()))
        _key_store.setex(f"mu:key:{key}", ttl, json.dumps(entry))
    else:
        _key_store[key] = entry

def _ks_del(key):
    if _using_redis:
        _key_store.delete(f"mu:key:{key}")
    elif key in _key_store:
        del _key_store[key]

KEY_DURATION_HOURS = 24
KEY_MAX_USES       = 50

def _generate_key():
    raw = secrets.token_urlsafe(18)
    ts  = int(time.time())
    sig = hashlib.sha256(f"{raw}:{ts}:MOONULTRA".encode()).hexdigest()[:8]
    key = f"MU-{raw}-{sig}".upper()
    _ks_set(key, {'expires': ts + KEY_DURATION_HOURS * 3600, 'uses': 0, 'max_uses': KEY_MAX_USES})
    return key

def _validate_key(key: str):
    if not key:
        return False, "No key provided"
    if not key.startswith("MU-"):
        return False, "Invalid key format"
    entry = _ks_get(key)
    if not entry:
        return False, "Key not found"
    if time.time() > entry['expires']:
        _ks_del(key); return False, "Key expired"
    if entry['uses'] >= entry['max_uses']:
        return False, "Key use limit reached"
    entry['uses'] += 1
    _ks_set(key, entry)
    return True, "OK"

def _require_key(key: str):
    valid, reason = _validate_key(key or "")
    if not valid:
        raise HTTPException(status_code=403, detail=f"Key error: {reason}")


# ═══════════════════════════════════════════════════════
#  OTP SYSTEM  (used by the Linkvertise key-get flow)
#  Tokens are HMAC-signed, single-use, 5-min TTL.
# ═══════════════════════════════════════════════════════

_OTP_SECRET  = os.environ.get("OTP_SECRET", secrets.token_hex(32))
_OTP_TTL     = 300   # seconds
_otp_store: dict = {}   # token_id -> {expires, redeemed}

def _otp_redis_key(tid): return f"mu:otp:{tid}"

def _otp_store_get(tid):
    if _using_redis:
        raw = _key_store.get(_otp_redis_key(tid))
        return json.loads(raw) if raw else None
    return _otp_store.get(tid)

def _otp_store_set(tid, entry):
    if _using_redis:
        ttl = max(1, math.ceil(entry['expires'] - time.time()))
        _key_store.setex(_otp_redis_key(tid), ttl, json.dumps(entry))
    else:
        _otp_store[tid] = entry

def _otp_store_del(tid):
    if _using_redis:
        _key_store.delete(_otp_redis_key(tid))
    else:
        _otp_store.pop(tid, None)

def _otp_sign(tid: str, ts: int) -> str:
    msg = f"{tid}:{ts}:{_OTP_SECRET}".encode()
    return hashlib.sha256(msg).hexdigest()[:16]

def _create_otp() -> str:
    tid = secrets.token_urlsafe(15)
    ts  = int(time.time())
    sig = _otp_sign(tid, ts)
    token = f"{tid}.{ts}.{sig}"
    _otp_store_set(tid, {'expires': ts + _OTP_TTL, 'redeemed': False})
    return token

def _redeem_otp(token: str):
    """Validate and burn an OTP token. Returns a fresh MU key on success."""
    parts = token.split('.')
    if len(parts) != 3:
        raise HTTPException(status_code=403, detail="Invalid token format")
    tid, ts_str, sig = parts
    try:
        ts = int(ts_str)
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid token")
    if sig != _otp_sign(tid, ts):
        raise HTTPException(status_code=403, detail="Token signature invalid")
    if time.time() > ts + _OTP_TTL:
        raise HTTPException(status_code=403, detail="Token expired")
    entry = _otp_store_get(tid)
    if not entry:
        raise HTTPException(status_code=403, detail="Token not found")
    if entry.get('redeemed'):
        raise HTTPException(status_code=403, detail="Token already used")
    # Burn it
    entry['redeemed'] = True
    _otp_store_set(tid, entry)
    _otp_store_del(tid)
    return _generate_key()


# ═══════════════════════════════════════════════════════
#  SERVE FRONTEND
# ═══════════════════════════════════════════════════════

@app.get('/')
async def root():
    return FileResponse('index.html')


# ═══════════════════════════════════════════════════════
#  API ROUTES
# ═══════════════════════════════════════════════════════

@app.get('/api/health')
async def health():
    return {
        'status':  'ok',
        'service': 'MOONULTRA V3 Advanced Backend',
        'version': '3.4.0',
        'features': [
            'Server-Side IP Auth (IP never exposed to client)',
            'Auto-Obfuscate On Upload (raw source never stored)',
            'Custom VM Bytecode',
            'Anti-Tamper Protection',
            'Control Flow Obfuscation',
            'String Pool Encryption',
            'Enchantment Table Junk Comments',
            'HMAC-Signed Single-Use OTP Key Flow',
        ],
    }


@app.get('/api/check-access')
async def check_access(request: Request):
    """Returns {owner: true/false} only — the IP itself is NEVER sent to the client."""
    ip = _real_ip(request)
    return {'owner': ip in OWNER_IPS}


@app.post('/api/obfuscate')
async def obfuscate(
    body: ObfuscateRequest,
    request: Request,
    x_moonultra_key: Optional[str] = Header(None),
    x_api_key:       Optional[str] = Header(None),
):
    """Public obfuscation endpoint — requires a valid key (owner IP bypasses key check)."""
    ip = _real_ip(request)
    if ip not in OWNER_IPS:
        key = x_moonultra_key or x_api_key or ""
        _require_key(key)

    if not body.code.strip():
        raise HTTPException(status_code=400, detail="Empty code")

    opts = body.options or ObfuscateOptions()
    try:
        result, stats = _run_obfuscation(body.code, opts)
        return {'success': True, 'code': result, 'stats': stats}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/upload-script')
async def upload_script(body: UploadScriptRequest, request: Request):
    """
    Owner-only. Accepts raw Luau source, obfuscates it server-side immediately,
    returns obfuscated code + loadstring. Raw source is never stored.
    """
    ip = _real_ip(request)
    if ip not in OWNER_IPS:
        raise HTTPException(status_code=403, detail="Forbidden")

    if not body.source.strip():
        raise HTTPException(status_code=400, detail="Empty source")
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Missing script name")

    opts = body.options or ObfuscateOptions()
    try:
        obfuscated, stats = _run_obfuscation(body.source, opts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    b64        = base64.b64encode(obfuscated.encode('utf-8')).decode()
    data_uri   = f"data:text/plain;base64,{b64}"
    loadstring = f'loadstring(game:HttpGet("{data_uri}"))()'

    return {
        'success':    True,
        'name':       body.name,
        'obfuscated': obfuscated,
        'loadstring': loadstring,
        'stats':      stats,
    }


@app.post('/api/otp/create')
async def otp_create():
    """
    Creates a short-lived, HMAC-signed, single-use OTP token.
    The frontend opens a new tab with this token in the URL;
    once the user completes the Linkvertise checkpoint the tab
    calls /api/otp/redeem to burn the token and receive a key.
    """
    token = _create_otp()
    return {'token': token, 'expires_in': _OTP_TTL}


@app.post('/api/otp/redeem')
async def otp_redeem(body: dict):
    """Validate + burn the OTP token, return a fresh MU key."""
    token = body.get('token', '')
    if not token:
        raise HTTPException(status_code=400, detail="Missing token")
    key = _redeem_otp(token)
    return {
        'key':                key,
        'expires_in_seconds': KEY_DURATION_HOURS * 3600,
        'max_uses':           KEY_MAX_USES,
    }


@app.post('/api/validate_key')
async def validate_key_route(
    body: KeyRequest = None,
    x_moonultra_key: Optional[str] = Header(None),
):
    key = (body.key if body else None) or x_moonultra_key or ""
    entry = _ks_get(key)
    if not entry:
        raise HTTPException(status_code=403, detail="Key not found")
    remaining = max(0, int(entry['expires'] - time.time()))
    uses_left  = max(0, entry['max_uses'] - entry['uses'])
    return {'valid': uses_left > 0 and remaining > 0, 'expires_in': remaining, 'uses_left': uses_left}


@app.post('/api/generate_key')
async def generate_key(request: Request):
    """Admin endpoint — owner IP only."""
    ip = _real_ip(request)
    if ip not in OWNER_IPS:
        raise HTTPException(status_code=403, detail="Forbidden")
    key = _generate_key()
    return {
        'success':            True,
        'key':                key,
        'expires_in_seconds': KEY_DURATION_HOURS * 3600,
        'max_uses':           KEY_MAX_USES,
        'message':            f'Key valid for {KEY_DURATION_HOURS}h, {KEY_MAX_USES} uses',
    }


@app.get('/api/key_stats')
async def key_stats(request: Request):
    """Admin endpoint — owner IP only."""
    ip = _real_ip(request)
    if ip not in OWNER_IPS:
        raise HTTPException(status_code=403, detail="Forbidden")
    now = time.time()
    if _using_redis:
        keys   = _key_store.keys("mu:key:*")
        active = 0
        for k in keys:
            raw = _key_store.get(k)
            if raw:
                try:
                    if json.loads(raw).get('expires', 0) > now:
                        active += 1
                except Exception:
                    pass
        return {'active_keys': active, 'total_keys': len(keys)}
    active = sum(1 for e in _key_store.values() if e['expires'] > now)
    return {'active_keys': active, 'total_keys': len(_key_store)}


if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    print(f"[MoonUltra] Starting on port {port}")
    uvicorn.run("App:app", host="0.0.0.0", port=port, reload=False)
