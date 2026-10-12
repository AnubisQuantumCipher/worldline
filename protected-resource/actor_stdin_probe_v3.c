#include <errno.h>
#include <stddef.h>
#include <unistd.h>

/* Unrun data fixture only. Full stdout must be collected; no digest, prefix,
 * byte count, actor policy or resource-authority substitute is emitted. */
int main(void) {
    unsigned char data[65536];
    for (;;) {
        ssize_t got;
        do { got=read(STDIN_FILENO,data,sizeof(data)); }
        while(got<0 && errno==EINTR);
        if(got<0)return 1;
        if(got==0)return 0;
        size_t offset=0;
        while(offset<(size_t)got) {
            ssize_t sent;
            do { sent=write(STDOUT_FILENO,data+offset,(size_t)got-offset); }
            while(sent<0 && errno==EINTR);
            if(sent<=0)return 1;
            offset+=(size_t)sent;
        }
    }
}
