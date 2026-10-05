/* WORLDLINE Phase One — W-1 frame-v6w1 N-owner / idmap-namespace helper (DRAFTING source).
 *
 * FROZEN, REVIEWABLE, UNINSTALLED. Author: Claude (Opus 4.8), DRAFTING implementer, not a
 * reviewer. Establishes no premise; COMPILED NOWHERE and EXECUTED NOWHERE in this session.
 *
 * Role (v11 §3.2 "RL's helpers", §12.2 step 10, §5.3). RL (sandbox_launch.py, root, stage 2)
 * forks one short-lived helper per user namespace it needs:
 *   - U8  : the owner of the target's view user namespace. RL then writes U8's setgroups=allow,
 *           uid_map and gid_map "0 0 4294967295" (identity, every id maps to itself; JACKAL exact
 *           4294967295 = 2^32-1, highest id 4294967294 = 4294967295-1, v11 §12.2 step 10).
 *   - M_run: the idmap userns of the two binds, which NO process ever enters; RL writes its
 *           uid_map and gid_map "W 1000 1" (v11 §12.2 step 10).
 * The helper's entire job is to assume identity N and create ONE user namespace whose OWNER is N
 * (the euid at unshare(CLONE_NEWUSER) time, v11 §3.1: "No process runs as N except RL's helper,
 * which creates the namespace and exits"). It then yields so RL — root in the parent namespace —
 * can open /proc/<helper>/ns/user, write the maps, and signal it to exit. "the helper runs no
 * other code" (v11 §12.2 step 10); "a plain fork of RL; no user@N.service" (v11 §5.3).
 *
 * This is the SANDBOX's OWN enforcement machinery (defensive). It attacks nothing, defeats no
 * boundary, and contains no exploit or refutation procedure. The premise P-NOOWNER it SERVES
 * ("no process other than RL's helper ever has euid N ... and the helper exits before L exists",
 * v11 §9.8 N7) is NAMED_UNESTABLISHED and stays OPEN: writing this helper is not its discharge.
 * Discharge is the operator's reviewed runtime census + root scan (I-1) and the §5.3 route
 * inventory (S-5/O-1); refutation is operator-reserved.
 *
 * Protocol with RL (fixed inherited descriptors; RL sets them up as pipes before fork/exec):
 *   fd 3  (READY, helper -> RL): after unshare succeeds the helper writes exactly one byte.
 *   fd 4  (GO,    RL -> helper): the helper then blocks on a one-byte read; RL writes the maps,
 *                                then writes one byte here; the helper _exit(0)s. RL reaps it and
 *                                re-reads /proc for the helper pid, requiring it gone before L
 *                                exists (v11 §12.2 step 10).
 * argv[1] = the numeric id to assume for BOTH uid and gid (N for U8 and for M_run; RL passes it).
 *
 * On ANY failure the helper writes an errno line to fd 2 and _exit()s non-zero WITHOUT having
 * created a usable namespace, so RL's stage-2 refuses (v11 §12.2 "Failures") before RL_IDENTITY.
 *
 * Build (operator/staging only; recorded, NOT run here):
 *   cc -O2 -std=c11 -Wall -Wextra -Werror -static-pie -o nsowner_helper nsowner_helper.c
 * and the resulting binary's bytes/sha256 are pinned in the installed frame inventory and in
 * RL_IDENTITY (v11 §3.2, §12.2). The installed invocation path and argv are reviewed with RL.
 */
#define _GNU_SOURCE
#include <sched.h>
#include <sys/prctl.h>
#include <sys/types.h>
#include <grp.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

enum { FD_READY = 3, FD_GO = 4 };

static void die(const char *what)
{
    /* one errno line to stderr; no other output, no cleanup that could touch a filesystem */
    char buf[128];
    int e = errno;
    size_t n = 0;
    const char *p = what;
    while (*p && n < sizeof(buf) - 16) buf[n++] = *p++;
    buf[n++] = ' ';
    /* minimal base-10 errno, no libc stdio */
    char num[16]; int ni = 0; if (e == 0) num[ni++] = '0';
    while (e > 0 && ni < (int)sizeof(num)) { num[ni++] = (char)('0' + e % 10); e /= 10; }
    while (ni > 0) buf[n++] = num[--ni];
    buf[n++] = '\n';
    (void)!write(2, buf, n);
    _exit(1);
}

int main(int argc, char **argv)
{
    if (argc != 2) { (void)!write(2, "usage\n", 6); _exit(2); }

    errno = 0;
    long id = strtol(argv[1], NULL, 10);
    if (id <= 0 || id > 2147483647L) { (void)!write(2, "bad-id\n", 7); _exit(2); }
    gid_t g = (gid_t)id;
    uid_t u = (uid_t)id;

    /* v11 §12.2 step 10, in this exact order: drop all supplementary groups, assume gid N in all
     * three positions, then uid N in all three positions, mark non-dumpable, then unshare the user
     * namespace so its owner is N. Each is checked; a failure refuses before any namespace exists. */
    if (setgroups(0, NULL) != 0)               die("setgroups");
    if (setresgid(g, g, g) != 0)               die("setresgid");
    if (setresuid(u, u, u) != 0)               die("setresuid");
    if (prctl(PR_SET_DUMPABLE, 0L, 0L, 0L, 0L) != 0) die("prctl_dumpable");
    if (unshare(CLONE_NEWUSER) != 0)           die("unshare_newuser");

    /* READY: tell RL the namespace exists so it can open /proc/<pid>/ns/user and write the maps. */
    {
        char one = '1';
        if (write(FD_READY, &one, 1) != 1) die("write_ready");
    }

    /* Block until RL has written setgroups/uid_map/gid_map and signals GO; then exit. The helper
     * runs no other code: it opens nothing, maps nothing itself, and never enters the namespace. */
    {
        char go = 0;
        ssize_t r = read(FD_GO, &go, 1);
        if (r < 0) die("read_go");
    }
    _exit(0);
}
