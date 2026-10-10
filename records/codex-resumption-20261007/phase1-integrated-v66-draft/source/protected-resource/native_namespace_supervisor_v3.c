#define _GNU_SOURCE
/* Additive source-only V3 protected descendant supervisor with owned
 * post-drop credential measurement and durable broker ACK before actor exec.
 * Original V1 and V2 remain byte/mode exact and separately selectable. This source
 * does not establish native/syscall semantics, custody or full body/cost proof.
 * Source-only protected descendant supervisor. No ordinary claimant may launch
 * this helper directly through the intent endpoint. The protected caller owns
 * the exact executable, kernel peer, namespace and pidfd descriptors, current
 * full native reservation, durable dispatch intent, and GO barrier.
 * A CLOSED record is emitted only after the namespace init reaped every child
 * and the outer helper actually waited for that init. EOF, kill, missing facts
 * or a failed write never emits CLOSED. This is not build/proof/runtime evidence.
 */
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include <linux/capability.h>
#include <linux/securebits.h>
#include <sched.h>
#include <signal.h>
#include <stdint.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <grp.h>
#include <limits.h>
#include <sys/stat.h>

struct closed_record { pid_t main_pid; int main_status; };
static void die(void) { _exit(125); }
static void write_all(int fd, const void *source, size_t length) {
    const unsigned char *p=source;
    while(length) { ssize_t n=write(fd,p,length); if(n<0 && errno==EINTR)continue;
        if(n<=0)die(); p+=n; length-=(size_t)n; }
}
static void read_all(int fd, void *target, size_t length) {
    unsigned char *p=target;
    while(length) { ssize_t n=read(fd,p,length); if(n<0 && errno==EINTR)continue;
        if(n<=0)die(); p+=n; length-=(size_t)n; }
}
static uintmax_t identifier(const char *word) {
    char *end; errno=0;
    if(!word[0] || word[0]=='-' || word[0]=='+')die();
    for(const char *p=word;*p;++p)if(*p<'0'||*p>'9')die();
    uintmax_t n=strtoumax(word,&end,10); if(errno || *end)die(); return n;
}
static void drop(uid_t uid,gid_t gid) {
    /* No capability, supplementary group or root credential reaches the actor.
     * Nested user/PID namespaces remain descendants of this namespace init;
     * setns into an ancestor PID/user namespace lacks its owning capability.
     */
    for (int cap = 0;;) {
        errno = 0;
        int present = prctl(PR_CAPBSET_READ, cap, 0, 0, 0);
        if (present < 0 && errno == EINVAL) break;
        if (present < 0 || prctl(PR_CAPBSET_DROP, cap, 0, 0, 0) < 0) die();
        if (cap == INT_MAX) die();
        ++cap;
    }
    if(prctl(PR_SET_SECUREBITS,SECBIT_NOROOT|SECBIT_NOROOT_LOCKED|
             SECBIT_NO_SETUID_FIXUP|SECBIT_NO_SETUID_FIXUP_LOCKED,0,0,0)<0)die();
    if(setgroups(0,NULL)<0 || setresgid(gid,gid,gid)<0 || setresuid(uid,uid,uid)<0)die();
    struct __user_cap_header_struct header={_LINUX_CAPABILITY_VERSION_3,0};
    struct __user_cap_data_struct data[2]={{0,0,0},{0,0,0}};
    if(syscall(SYS_capset,&header,data)<0 || prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0)<0)die();
}

/* The receiver is passed to the already authenticated protected broker before
 * GO. Only this trusted child retains the sender before exec. Source identity
 * and channel bytes alone are not credential/custody or native-policy proof. */
struct cap_observation { int bounding; int ambient; };

static void close_received_rights(struct msghdr *message) {
    for (struct cmsghdr *c = CMSG_FIRSTHDR(message); c;
         c = CMSG_NXTHDR(message, c)) {
        if (c->cmsg_level == SOL_SOCKET && c->cmsg_type == SCM_RIGHTS &&
            c->cmsg_len >= CMSG_LEN(0)) {
            size_t size = c->cmsg_len - CMSG_LEN(0);
            for (size_t offset = 0; size - offset >= sizeof(int);
                 offset += sizeof(int)) {
                int fd;
                memcpy(&fd, (unsigned char *)CMSG_DATA(c) + offset, sizeof(fd));
                close(fd);
            }
        }
    }
}

static size_t packet_size_field(const unsigned char *body, size_t length,
                               size_t *position) {
    if (*position >= length) die();
    size_t start = *position;
    while (*position < length && body[*position] != '\n') {
        if (body[*position] < '0' || body[*position] > '9') die();
        ++*position;
    }
    if (*position == start || *position == length ||
        (body[start] == '0' && *position - start != 1)) die();
    size_t digits = *position - start;
    if (digits == SIZE_MAX) die();
    char *word = malloc(digits + 1);
    if (!word) die();
    memcpy(word, body + start, digits); word[digits] = 0;
    uintmax_t number = identifier(word); free(word);
    if (number > SIZE_MAX) die();
    ++*position;
    return (size_t)number;
}

static void wait_credential_commit(int fd, const unsigned char *frame,
                                   size_t frame_length) {
    ssize_t extent;
    do { extent = recv(fd, NULL, 0, MSG_PEEK | MSG_TRUNC); }
    while (extent < 0 && errno == EINTR);
    if (extent <= 0) die();
    unsigned char *body = malloc((size_t)extent);
    if (!body) die();
    struct iovec iov = {body, (size_t)extent};
    union { struct cmsghdr align;
        unsigned char bytes[CMSG_SPACE(sizeof(struct ucred))+CMSG_SPACE(sizeof(int))]; } control = {0};
    struct msghdr message = {.msg_iov=&iov, .msg_iovlen=1,
        .msg_control=control.bytes, .msg_controllen=sizeof(control.bytes)};
    ssize_t received;
    do { received = recvmsg(fd, &message, MSG_CMSG_CLOEXEC); }
    while (received < 0 && errno == EINTR);
    int witness_fd = -1, credentials_seen = 0, rights_seen = 0, malformed = 0;
    struct ucred sender = {0};
    for (struct cmsghdr *c=CMSG_FIRSTHDR(&message); c;
         c=CMSG_NXTHDR(&message,c)) {
        if (c->cmsg_level == SOL_SOCKET && c->cmsg_type == SCM_CREDENTIALS &&
            c->cmsg_len == CMSG_LEN(sizeof(sender)) && !credentials_seen) {
            memcpy(&sender,CMSG_DATA(c),sizeof(sender)); credentials_seen=1;
        } else if (c->cmsg_level == SOL_SOCKET && c->cmsg_type == SCM_RIGHTS &&
                   c->cmsg_len == CMSG_LEN(sizeof(int)) && !rights_seen) {
            memcpy(&witness_fd,CMSG_DATA(c),sizeof(witness_fd)); rights_seen=1;
        } else malformed=1;
    }
    if (received != extent || (message.msg_flags & (MSG_TRUNC | MSG_CTRUNC)) ||
        malformed || !credentials_seen || !rights_seen || witness_fd < 0) {
        close_received_rights(&message); die();
    }
    /* The owning broker explicitly sends its actual effective root credential.
     * An outside-PID-namespace sender can correctly appear with PID zero here.
     * The inherited sole endpoint and the original root-owner HELD channel
     * supply the required channel join; PID zero never proves process death. */
    if (sender.uid != 0) die();
    static const unsigned char header[] = "WL-RESOURCE-ACTOR-COMMIT-v1\n";
    size_t length = (size_t)received;
    if (length < sizeof(header)-1 || memcmp(body,header,sizeof(header)-1)) die();
    size_t position = sizeof(header)-1;
    size_t echo = packet_size_field(body,length,&position);
    if (echo != frame_length || echo > length-position ||
        memcmp(body+position,frame,echo)) die();
    position += echo;
    size_t witness = packet_size_field(body,length,&position);
    if (!witness || position != length) die();
    struct stat info;
    int seals=fcntl(witness_fd,F_GET_SEALS);
    int required=F_SEAL_SEAL|F_SEAL_SHRINK|F_SEAL_GROW|F_SEAL_WRITE;
    if (fstat(witness_fd,&info)<0 || !S_ISREG(info.st_mode) || info.st_uid!=0 ||
        info.st_size<=0 || (uintmax_t)info.st_size!=(uintmax_t)witness ||
        seals<0 || (seals&required)!=required) die();
    /* Read the entire immutable witness without a fixed datagram or semantic
     * length cap. The literal chunk is the existing bounded display size.
     * Complete source/native decision/durable custody remain caller obligations;
     * an opaque sealed file, digest or receipt does not invent permission.
     */
    unsigned char chunk[65536];
    off_t offset=0;
    while (offset<info.st_size) {
        off_t remaining=info.st_size-offset;
        size_t amount=remaining<(off_t)sizeof(chunk)?(size_t)remaining:sizeof(chunk);
        ssize_t copied;
        do { copied=pread(witness_fd,chunk,amount,offset); }
        while(copied<0 && errno==EINTR);
        if(copied<=0 || (size_t)copied>amount)die();
        offset+=copied;
    }
    if(close(witness_fd)<0)die();
    free(body);
}

static void measure_actor_and_wait(int fd, const char *ticket) {
    uid_t real_uid, effective_uid, saved_uid;
    gid_t real_gid, effective_gid, saved_gid;
    if (getresuid(&real_uid,&effective_uid,&saved_uid) < 0 ||
        getresgid(&real_gid,&effective_gid,&saved_gid) < 0) die();
    int group_count = getgroups(0,NULL);
    if (group_count < 0 || (size_t)group_count > SIZE_MAX/sizeof(gid_t)) die();
    gid_t *groups = group_count ? malloc((size_t)group_count*sizeof(gid_t)) : NULL;
    if (group_count && !groups) die();
    if (getgroups(group_count,groups) != group_count) die();
    struct __user_cap_header_struct cap_header = {_LINUX_CAPABILITY_VERSION_3,0};
    struct __user_cap_data_struct cap_words[2] = {{0,0,0},{0,0,0}};
    if (syscall(SYS_capget,&cap_header,cap_words) < 0 ||
        cap_header.version != _LINUX_CAPABILITY_VERSION_3 || cap_header.pid != 0) die();
    int securebits = prctl(PR_GET_SECUREBITS,0,0,0,0);
    int no_new_privs = prctl(PR_GET_NO_NEW_PRIVS,0,0,0,0);
    if (securebits < 0 || no_new_privs < 0) die();
    struct cap_observation *caps = NULL;
    size_t cap_count = 0;
    for (int cap = 0;;) {
        errno = 0;
        int bounding = prctl(PR_CAPBSET_READ,cap,0,0,0);
        if (bounding < 0 && errno == EINVAL) break;
        if (bounding < 0) die();
        int ambient = prctl(PR_CAP_AMBIENT,PR_CAP_AMBIENT_IS_SET,cap,0,0);
        if (ambient < 0 || cap_count >= SIZE_MAX/sizeof(*caps)) die();
        struct cap_observation *next = realloc(caps,(cap_count+1)*sizeof(*caps));
        if (!next) die();
        caps = next;
        caps[cap_count].bounding=bounding; caps[cap_count].ambient=ambient;
        ++cap_count;
        if (cap == INT_MAX) die();
        ++cap;
    }
    char *frame = NULL;
    size_t extent = 0;
    FILE *stream = open_memstream(&frame,&extent);
    if (!stream) die();
    if (fprintf(stream,"WL-RESOURCE-ACTOR-CREDENTIALS-v1\n%s\n%jd\n"
        "%ju\n%ju\n%ju\n%ju\n%ju\n%ju\n%" PRIu32 "\n",
        ticket,(intmax_t)getpid(),(uintmax_t)real_uid,(uintmax_t)effective_uid,
        (uintmax_t)saved_uid,(uintmax_t)real_gid,(uintmax_t)effective_gid,
        (uintmax_t)saved_gid,cap_header.version) < 0) die();
    for (size_t i=0;i<sizeof(cap_words)/sizeof(cap_words[0]);++i)
        if (fprintf(stream,"%" PRIu32 "\n%" PRIu32 "\n%" PRIu32 "\n",
            cap_words[i].effective,cap_words[i].permitted,cap_words[i].inheritable) < 0) die();
    if (fprintf(stream,"%d\n%d\n%zu\n",securebits,no_new_privs,cap_count) < 0) die();
    for (size_t i=0;i<cap_count;++i)
        if (fprintf(stream,"%zu\n%d\n%d\n",i,caps[i].bounding,caps[i].ambient) < 0) die();
    if (fprintf(stream,"%d\n",group_count) < 0) die();
    for (int i=0;i<group_count;++i)
        if (fprintf(stream,"%ju\n",(uintmax_t)groups[i]) < 0) die();
    if (fprintf(stream,"END\n") < 0 || ferror(stream)) die();
    if (fclose(stream) != 0) die();
    free(caps); free(groups);
    ssize_t sent;
    do { sent=send(fd,frame,extent,MSG_NOSIGNAL); } while(sent<0 && errno==EINTR);
    if (sent < 0 || (size_t)sent != extent) die();
    wait_credential_commit(fd,(const unsigned char *)frame,extent);
    free(frame);
    if (close(fd) < 0) die();
}

static int connect_owner(const char *path) {
    struct sockaddr_un name={.sun_family=AF_UNIX};
    size_t length=strlen(path); if(!length || length>=sizeof(name.sun_path))die();
    memcpy(name.sun_path,path,length+1);
    int fd=socket(AF_UNIX,SOCK_SEQPACKET|SOCK_CLOEXEC,0); if(fd<0)die();
    if(connect(fd,(struct sockaddr *)&name,offsetof(struct sockaddr_un,sun_path)+length+1)<0)die();
    struct ucred peer; socklen_t size=sizeof(peer);
    if(getsockopt(fd,SOL_SOCKET,SO_PEERCRED,&peer,&size)<0 || size!=sizeof(peer) || peer.pid<=0 || peer.uid!=0)die();
    return fd;
}
static void hello(int socket_fd,const char *ticket,pid_t init,int namespace_fd,int pidfd,int out,int err,int actor_receiver,int stdin_writer) {
    char *body=NULL;
    int length=asprintf(&body,"WL-RESOURCE-SUPERVISOR-v3\nHELD\n%s\n%jd\n",ticket,(intmax_t)init);
    if(length<0)die();
    struct iovec iov={body,(size_t)length};
    union {struct cmsghdr align; unsigned char bytes[CMSG_SPACE(sizeof(int)*6)];} control={0};
    struct msghdr message={.msg_iov=&iov,.msg_iovlen=1,.msg_control=control.bytes,.msg_controllen=sizeof(control.bytes)};
    struct cmsghdr *cmsg=CMSG_FIRSTHDR(&message); cmsg->cmsg_level=SOL_SOCKET;cmsg->cmsg_type=SCM_RIGHTS;
    cmsg->cmsg_len=CMSG_LEN(sizeof(int)*6); int fds[6]={namespace_fd,pidfd,out,err,actor_receiver,stdin_writer};memcpy(CMSG_DATA(cmsg),fds,sizeof(fds));
    ssize_t n;do{n=sendmsg(socket_fd,&message,MSG_NOSIGNAL);}while(n<0&&errno==EINTR);
    if(n!=length)die(); free(body);
}
static void namespace_init(int go,int report,int out,int err,int actor_sender,int actor_stdin,const char *ticket,uid_t uid,gid_t gid,const char *cwd,
                           int env_begin,int env_end,char **complete,char **argv) {
    if(getpid()!=1 || prctl(PR_SET_CHILD_SUBREAPER,1,0,0,0)<0)die();
    /* Mount proc for this actual PID namespace in a separate private mount
     * namespace. The outer helper keeps host proc for its owned descriptors.
     * Failure is unknown, never an asserted descendant closure. */
    if(unshare(CLONE_NEWNS)<0 || mount(NULL,"/",NULL,MS_REC|MS_PRIVATE,NULL)<0 ||
       mount("proc","/proc","proc",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL)<0)die();
    /* Before GO only the trusted namespace init exists. The actor cannot run
     * before the parent durably committed the full native Running transition.
     */
    unsigned char ready='H';write_all(report,&ready,sizeof(ready));
    unsigned char command;read_all(go,&command,sizeof(command)); if(command!='G')die();
    close(go);
    pid_t child=fork();if(child<0)die();
    if(child==0){
        close(report);
        /* Owned input was created before fork. Only this read endpoint reaches
         * the actor. No stdin byte is read or bounded by this supervisor; the
         * protected broker owns the sole write endpoint and exact EOF. */
        if(dup2(actor_stdin,STDIN_FILENO)<0)die();
        if(actor_stdin!=STDIN_FILENO && close(actor_stdin)<0)die();
        if(dup2(out,STDOUT_FILENO)<0 || dup2(err,STDERR_FILENO)<0)die();
        close(out);close(err);drop(uid,gid);
        measure_actor_and_wait(actor_sender,ticket);
        if(chdir(cwd)<0 || clearenv()<0)die();
        for(int i=env_begin;i<env_end;i+=3)
            if(setenv(complete[i+1],complete[i+2],1)<0)die();
        execvp(argv[0],argv);die();
    }
    if(close(actor_stdin)<0)die();
    close(out);close(err);close(actor_sender);
    struct closed_record record={.main_pid=child,.main_status=0};int saw_main=0;
    for(;;){int status;pid_t reaped=waitpid(-1,&status,0);
        if(reaped<0 && errno==EINTR)continue;
        if(reaped<0 && errno==ECHILD)break;
        if(reaped<=0)die();
        if(reaped==child){if(saw_main)die();saw_main=1;record.main_status=status;}}
    if(!saw_main)die();
    /* PID 1 has no remaining child or orphan descendant, and this trusted code
     * performs no further fork/clone/exec. The outer helper separately waits it.
     */
    write_all(report,&record,sizeof(record));close(report);_exit(0);
}
int main(int argc,char **argv) {
    if(argc<8 || geteuid()!=0 || argv[5][0]!='/')die();
    int end=6;
    while(end<argc && !strcmp(argv[end],"--env")) {
        if(argc-end<3 || !argv[end+1][0])die();
        const char *name=argv[end+1];
        if(!((name[0]>='A'&&name[0]<='Z')||(name[0]>='a'&&name[0]<='z')||name[0]=='_'))die();
        for(const char *p=name+1;*p;++p)
            if(!((*p>='A'&&*p<='Z')||(*p>='a'&&*p<='z')||(*p>='0'&&*p<='9')||*p=='_'))die();
        end+=3;
    }
    if(end>=argc-1 || strcmp(argv[end],"--") || !argv[end+1][0])die();
    const char *endpoint=argv[1],*ticket=argv[2];
    if(!ticket[0] || strchr(ticket,'\n') || strchr(ticket,'\r'))die();
    uintmax_t u=identifier(argv[3]),g=identifier(argv[4]);
    uid_t uid=(uid_t)u;gid_t gid=(gid_t)g;if(uid==0 || (uintmax_t)uid!=u || (uintmax_t)gid!=g)die();
    int owner=connect_owner(endpoint),go[2],report[2],out[2],err[2],actor[2],actor_stdin[2];
    if(socketpair(AF_UNIX,SOCK_SEQPACKET|SOCK_CLOEXEC,0,actor)<0)die();
    int passcred=1;
    if(setsockopt(actor[0],SOL_SOCKET,SO_PASSCRED,&passcred,sizeof(passcred))<0 ||
       setsockopt(actor[1],SOL_SOCKET,SO_PASSCRED,&passcred,sizeof(passcred))<0)die();
    if(pipe2(go,O_CLOEXEC)<0 || pipe2(report,O_CLOEXEC)<0 ||
       pipe2(out,O_CLOEXEC)<0 || pipe2(err,O_CLOEXEC)<0)die();
    /* Create both owned input endpoints before namespace fork. The helper
     * never buffers or transforms the arbitrary full actor byte stream. */
    if(pipe2(actor_stdin,O_CLOEXEC)<0)die();
    if(unshare(CLONE_NEWPID)<0)die();
    pid_t init=fork();if(init<0)die();
    if(init==0){close(owner);close(actor[0]);close(go[1]);close(report[0]);close(out[0]);close(err[0]);
        if(close(actor_stdin[1])<0)die();
        namespace_init(go[0],report[1],out[1],err[1],actor[1],actor_stdin[0],ticket,uid,gid,argv[5],6,end,argv,&argv[end+1]);die();}
    if(close(actor_stdin[0])<0)die();
    close(go[0]);close(report[1]);close(out[1]);close(err[1]);close(actor[1]);
    unsigned char ready;read_all(report[0],&ready,sizeof(ready));if(ready!='H')die();
    int pidfd=(int)syscall(SYS_pidfd_open,init,0); if(pidfd<0)die();
    char *path=NULL;if(asprintf(&path,"/proc/%jd/ns/pid",(intmax_t)init)<0)die();
    int ns=open(path,O_RDONLY|O_CLOEXEC);free(path);if(ns<0)die();
    hello(owner,ticket,init,ns,pidfd,out[0],err[0],actor[0],actor_stdin[1]);
    if(close(actor_stdin[1])<0)die();
    close(ns);close(out[0]);close(err[0]);close(actor[0]);
    unsigned char command;ssize_t n;
    do{n=recv(owner,&command,sizeof(command),0);}while(n<0&&errno==EINTR);
    if(n!=sizeof(command) || command!='G'){
        syscall(SYS_pidfd_send_signal,pidfd,SIGKILL,NULL,0);die();}
    write_all(go[1],&command,sizeof(command));close(go[1]);
    struct closed_record record;read_all(report[0],&record,sizeof(record));
    unsigned char extra;if(read(report[0],&extra,sizeof(extra))!=0)die();close(report[0]);
    int status;pid_t waited;do{waited=waitpid(init,&status,0);}while(waited<0&&errno==EINTR);
    if(waited!=init || !WIFEXITED(status) || WEXITSTATUS(status)!=0)die();close(pidfd);
    char *body=NULL;int length=asprintf(&body,"WL-RESOURCE-SUPERVISOR-v3\nCLOSED\n%s\n%jd\n%d\nECHILD\n",ticket,(intmax_t)init,record.main_status);
    if(length<0)die();do{n=send(owner,body,(size_t)length,MSG_NOSIGNAL);}while(n<0&&errno==EINTR);
    if(n!=length)die();free(body);
    /* Retain the closed frame before the helper goes terminal. Losing this ACK
     * cannot create a second launch or a CLOSED record on a future process.
     */
    do{n=recv(owner,&command,sizeof(command),0);}while(n<0&&errno==EINTR);
    if(n!=sizeof(command)||command!='A')die();close(owner);
    if(WIFEXITED(record.main_status))return WEXITSTATUS(record.main_status);
    if(WIFSIGNALED(record.main_status)){int sig=WTERMSIG(record.main_status);signal(sig,SIG_DFL);raise(sig);die();}
    die();
}
