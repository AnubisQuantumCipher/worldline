/* Synthetic tee-only syscall fault fixture; never injected into product/Bash. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static unsigned int write_count;
static int mode_is(const char *expected)
{
    const char *mode = getenv("CAPTURE_FAULT");
    return mode != NULL && strcmp(mode, expected) == 0;
}

ssize_t write(int fd, const void *buf, size_t count)
{
    ssize_t (*real_write)(int, const void *, size_t);
    void *symbol = dlsym(RTLD_NEXT, "write");
    if (symbol == NULL) { errno = EIO; return -1; }
    _Static_assert(sizeof(real_write) == sizeof(symbol), "POSIX function pointer ABI");
    memcpy(&real_write, &symbol, sizeof(real_write));
    if (fd == STDOUT_FILENO) {
        if (mode_is("first_eio")) { errno = EIO; return -1; }
        if (mode_is("first_enospc")) { errno = ENOSPC; return -1; }
        if (mode_is("partial")) {
            if (write_count != 0U) { errno = ENOSPC; return -1; }
            write_count = 1U;
            if (count > 1U) { return real_write(fd, buf, 1U); }
        }
        if (mode_is("lost_diag")) { errno = EIO; return -1; }
    }
    if (fd == STDERR_FILENO && mode_is("lost_diag")) { errno = ENOSPC; return -1; }
    return real_write(fd, buf, count);
}

int close(int fd)
{
    int (*real_close)(int);
    void *symbol = dlsym(RTLD_NEXT, "close");
    int result;
    if (symbol == NULL) { errno = EIO; return -1; }
    _Static_assert(sizeof(real_close) == sizeof(symbol), "POSIX function pointer ABI");
    memcpy(&real_close, &symbol, sizeof(real_close));
    result = real_close(fd);
    if (fd == STDOUT_FILENO && mode_is("close")) { errno = EIO; return -1; }
    return result;
}

int fclose(FILE *stream)
{
    int (*real_fclose)(FILE *);
    void *symbol = dlsym(RTLD_NEXT, "fclose");
    int target = fileno(stream);
    int result;
    if (symbol == NULL) { errno = EIO; return EOF; }
    _Static_assert(sizeof(real_fclose) == sizeof(symbol), "POSIX function pointer ABI");
    memcpy(&real_fclose, &symbol, sizeof(real_fclose));
    result = real_fclose(stream);
    if (target == STDOUT_FILENO && mode_is("close")) { errno = EIO; return EOF; }
    return result;
}

/* GNU tee imports these stdio boundaries for diagnostics (glibc may hide write). */
#include <stdarg.h>
int __vfprintf_chk(FILE *stream, int flag, const char *format, va_list args)
{
    int (*real_call)(FILE *, int, const char *, va_list);
    void *symbol = dlsym(RTLD_NEXT, "__vfprintf_chk");
    if (symbol == NULL) { errno = EIO; return -1; }
    if (fileno(stream) == STDERR_FILENO && mode_is("lost_diag")) {
        errno = ENOSPC; return -1;
    }
    _Static_assert(sizeof(real_call) == sizeof(symbol), "POSIX function pointer ABI");
    memcpy(&real_call, &symbol, sizeof(real_call));
    return real_call(stream, flag, format, args);
}

int __fprintf_chk(FILE *stream, int flag, const char *format, ...)
{
    va_list args;
    int result;
    va_start(args, format);
    result = __vfprintf_chk(stream, flag, format, args);
    va_end(args);
    return result;
}

int fputs_unlocked(const char *text, FILE *stream)
{
    int (*real_call)(const char *, FILE *);
    void *symbol = dlsym(RTLD_NEXT, "fputs_unlocked");
    if (symbol == NULL) { errno = EIO; return EOF; }
    if (fileno(stream) == STDERR_FILENO && mode_is("lost_diag")) {
        errno = ENOSPC; return EOF;
    }
    _Static_assert(sizeof(real_call) == sizeof(symbol), "POSIX function pointer ABI");
    memcpy(&real_call, &symbol, sizeof(real_call));
    return real_call(text, stream);
}

size_t (fwrite_unlocked)(const void *ptr, size_t size, size_t count, FILE *stream)
{
    size_t (*real_call)(const void *, size_t, size_t, FILE *);
    void *symbol = dlsym(RTLD_NEXT, "fwrite_unlocked");
    if (symbol == NULL) { errno = EIO; return 0; }
    if (fileno(stream) == STDERR_FILENO && mode_is("lost_diag")) {
        errno = ENOSPC; return 0;
    }
    _Static_assert(sizeof(real_call) == sizeof(symbol), "POSIX function pointer ABI");
    memcpy(&real_call, &symbol, sizeof(real_call));
    return real_call(ptr, size, count, stream);
}

int fputc_unlocked(int value, FILE *stream)
{
    int (*real_call)(int, FILE *);
    void *symbol = dlsym(RTLD_NEXT, "fputc_unlocked");
    if (symbol == NULL) { errno = EIO; return EOF; }
    if (fileno(stream) == STDERR_FILENO && mode_is("lost_diag")) {
        errno = ENOSPC; return EOF;
    }
    _Static_assert(sizeof(real_call) == sizeof(symbol), "POSIX function pointer ABI");
    memcpy(&real_call, &symbol, sizeof(real_call));
    return real_call(value, stream);
}
