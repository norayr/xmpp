# XMPP tests

Run these commands from the VOC checkout:

```sh
make -C src/ports/xmpp test network-test tls-regression VOC="$PWD/install/bin/voc"
```

The offline tests cover UTF-16 code units, UTF-8 wire encoding, mixed XML
content, namespace scope, stream restarts, partial writes and session hooks.
They include 232 input split sizes, a 40,002-code-unit message and 665
TLS/SASL/binding negotiation checks. The snapshot check verifies all 88
preserved upstream files by size and SHA-256.

Twenty Python/OpenSSL loopback cases cover STARTTLS, direct TLS, Unicode
credentials, messages and domains, certificate and protocol-version rejection,
binding failures and stalled reads/handshakes. The shared IDNA suite has 38
conversion and rejection cases. The TLS regression target also runs the 36
existing TLS programs, HTTP/TLS loopback tests and 40 Gemini checks.

These pass on x86-64 Linux with GCC/C23, Clang/C23, TCC and Clang ASan/UBSan.
The sanitizer build uses an uninstrumented conservative core runtime, with
`ASAN_OPTIONS=detect_leaks=0:detect_stack_use_after_return=0` and
`UBSAN_OPTIONS=halt_on_error=1`. Shared IDNA and all 14 XMPP module consumers
also pass against a modular VOC image.

On 26 October 2026, a live account with an Armenian localpart and domain passed
verified STARTTLS on `xmpp.ծոց.հայ:5222`, PLAIN authentication, resource binding
to `/voc-մուտք`, an Armenian/supplementary self-message round trip and clean
shutdown. DNS discovery was performed separately. Credentials are supplied on
standard input and are absent from the result output.

Local validation logs in the VOC checkout:

- `build/xmpp-unicode-domain-{gcc,clang,tcc,sanitize}.log`
- `build/xmpp-unicode-domain-modular.log`
- `build/xmpp-idna-modelC.log`
- `build/xmpp-unicode-live.log`
- `build/xmpp-publishing-standalone.log` (standalone checkout and shared-TLS tests)
- `build/xmpp-publishing-modular.log` (default portable XMPP build and 285 ABI/load checks)

The XML/shared suites also pass: 14 XML programs, seven shared programs,
114 codec vectors, 77 URI fixtures, 2,687 conformance/output cases, 53 hostile
inputs and 2,655 deterministic mutation checks. XML stream coverage includes
486 additional mutations and lifetime/exact-consumption limits. Earlier full
suite logs are `build/xmpp-session-{gcc,clang,tcc,sanitize}.log`.
