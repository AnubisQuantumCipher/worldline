A concrete **future acquisition candidate exists in local package metadata**:

| Field | Observed value |
|---|---|
| Repository | Arch Linux ARM `extra` |
| Database | `/var/lib/pacman/sync/extra.db`, entry `strace-7.2-1/desc` |
| Database SHA256 | `eeb31a22fcdcc1911867715c278ab98e4b4a57954e85be654b60fbd7b84c8b74` |
| Version / architecture | `7.2-1` / `aarch64` |
| Package filename | `strace-7.2-1-aarch64.pkg.tar.xz` |
| Package SHA256 | `91c4ac1483cc7c14e1603b80cecfe51528b4d574c501d0fcd9f0e481d3efeac4` |
| Compressed / installed size | `438188` / `2123662` bytes |
| Packager | `Arch Linux ARM Build System <builder+n1@archlinuxarm.org>` |
| Build timestamp | `1789076460` |
| Embedded package signature | `%PGPSIG%` present; decoded size `566` bytes |
| Signature SHA256 | `31fccec2fd785771af91f5b926fcf01aa09bfb41bcb80b63f60ab78de4e31a6f` |

Configured mirror template is `http://mirror.archlinuxarm.org/$arch/$repo`, yielding the **prospective, uncontacted** URL:

`http://mirror.archlinuxarm.org/aarch64/extra/strace-7.2-1-aarch64.pkg.tar.xz`

Global policy is `SigLevel = Required DatabaseOptional`; `extra` inherits it. No `extra.db.sig` was listed. Consequently, database metadata alone does **not** authenticate the package. ARM keyring/trust files exist, but signer identity, trust, revocation status and signature validity were not checked.

No matching package exists directly under `/var/cache/pacman/pkg`; four private download directories were unreadable and remain UNKNOWN.

**Extraction into a later registered owned tool root is feasible in principle without host installation**, contingent on obtaining this exact package and authenticating it first. Later evidence must include package bytes matching the recorded SHA256, cryptographic signature verification against an independently trusted ARM signer, retained signer fingerprint/key evidence, safe archive-member validation, actual extracted executable/dependency inventory, and pinned local documentation. The database entry provides no dependency field; runtime compatibility remains UNTESTED.

**Smallest next step:** register a bounded acquisition and authenticity check for these exact bytes. This lookup authorizes no download, extraction, installation, runtime test or D47 launch. No writes or network access occurred.