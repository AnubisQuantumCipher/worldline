#define _GNU_SOURCE
#include "full_physical_actuator.h"
#include <sys/socket.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <stddef.h>
uint32_t wl_internal_full_physical_version_v1(void) { return 1; }
long wl_internal_full_physical_layout_v1(uint32_t kind,uint32_t field) {
#define HEAD(T) if (field==0) return sizeof(T); if (field==1) return _Alignof(T)
#define FIELD(T,N,F) if (field==N) return offsetof(T,F)
 if (kind==1) { HEAD(struct wl_entry_identity); FIELD(struct wl_entry_identity,2,present);
  FIELD(struct wl_entry_identity,3,device); FIELD(struct wl_entry_identity,4,inode); }
 if (kind==2) { HEAD(struct wl_actuation_request); FIELD(struct wl_actuation_request,2,collapse_facts);
  FIELD(struct wl_actuation_request,3,expected_live); FIELD(struct wl_actuation_request,4,observed_live);
  FIELD(struct wl_actuation_request,5,expected_stage); FIELD(struct wl_actuation_request,6,observed_stage);
  FIELD(struct wl_actuation_request,7,expected_marker_digest); FIELD(struct wl_actuation_request,8,observed_marker_digest);
  FIELD(struct wl_actuation_request,9,payload_durable); FIELD(struct wl_actuation_request,10,recovery_clean); }
 if (kind==3) { HEAD(struct wl_actuator_witness); FIELD(struct wl_actuator_witness,2,live_before);
  FIELD(struct wl_actuator_witness,3,stage_before); FIELD(struct wl_actuator_witness,4,live_after);
  FIELD(struct wl_actuator_witness,5,stage_after); FIELD(struct wl_actuator_witness,6,marker_digest);
  FIELD(struct wl_actuator_witness,7,decision); FIELD(struct wl_actuator_witness,8,exchange_attempted);
  FIELD(struct wl_actuator_witness,9,syscall_errno);
  FIELD(struct wl_actuator_witness,10,payload_durable); FIELD(struct wl_actuator_witness,11,recovery_clean);
  FIELD(struct wl_actuator_witness,12,parents_durable); }
 return -1;
#undef HEAD
#undef FIELD
}
#include <stdbool.h>
#include <errno.h>
#include <dirent.h>
#include <fcntl.h>

/* No depth, root, byte or file-count cap. The fixed buffer is an I/O chunk,
 * not a domain limit. Protected parent custody and writer quiescence remain
 * installed-principal obligations; fsync is an observed kernel durability
 * result, not a claim about untrusted storage hardware. */
static bool stable(const struct stat *a,const struct stat *b) {
 return a->st_dev==b->st_dev && a->st_ino==b->st_ino && a->st_mode==b->st_mode &&
  a->st_size==b->st_size && a->st_mtim.tv_sec==b->st_mtim.tv_sec &&
  a->st_mtim.tv_nsec==b->st_mtim.tv_nsec && a->st_ctim.tv_sec==b->st_ctim.tv_sec &&
  a->st_ctim.tv_nsec==b->st_ctim.tv_nsec;
}
static bool dot(const char *s) { return strcmp(s,".")==0 || strcmp(s,"..")==0; }
static bool durable_file(int fd) {
 struct stat before,after; unsigned char buffer[65536]; off_t used=0;
 if (fstat(fd,&before)!=0 || !S_ISREG(before.st_mode) || before.st_size<0 || fsync(fd)!=0) return false;
 for (;;) {
  ssize_t n=read(fd,buffer,sizeof(buffer));
  if (n<0) return false;
  if (n==0) break;
  if ((off_t)n>before.st_size-used) return false;
  used+=(off_t)n;
 }
 return used==before.st_size && fstat(fd,&after)==0 && stable(&before,&after);
}
static bool durable_tree(int fd) {
 struct stat before,after;
 if (fstat(fd,&before)!=0 || !S_ISDIR(before.st_mode)) return false;
 int scan=openat(fd,".",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
 if (scan<0) return false;
 DIR *directory=fdopendir(scan);
 if (directory==NULL) { close(scan); return false; }
 bool ok=true;
 for (;;) {
  errno=0; struct dirent *entry=readdir(directory);
  if (entry==NULL) { if (errno!=0) ok=false; break; }
  if (dot(entry->d_name)) continue;
  struct stat value,readback;
  if (fstatat(fd,entry->d_name,&value,AT_SYMLINK_NOFOLLOW)!=0) { ok=false; break; }
  if (S_ISDIR(value.st_mode) || S_ISREG(value.st_mode)) {
   int child=openat(fd,entry->d_name,O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK|
       (S_ISDIR(value.st_mode)?O_DIRECTORY:0));
   if (child<0) { ok=false; break; }
   struct stat opened;
   ok=fstat(child,&opened)==0 && stable(&value,&opened) &&
      (S_ISDIR(value.st_mode)?durable_tree(child):durable_file(child));
   int saved=errno; close(child); errno=saved;
   if (!ok) break;
  } else if (!S_ISLNK(value.st_mode)) { ok=false; break; }
  /* Nested symlinks are payload bytes, never traversed. The parent fsync
   * commits their directory entries, preserving original Manifest semantics. */
  if (fstatat(fd,entry->d_name,&readback,AT_SYMLINK_NOFOLLOW)!=0 || !stable(&value,&readback)) {
   ok=false; break;
  }
 }
 int saved=errno; closedir(directory); errno=saved;
 return ok && fsync(fd)==0 && fstat(fd,&after)==0 && stable(&before,&after);
}
static bool durable_mapping(int parent,const char *name,int payload_fd) {
 int fd=openat(parent,name,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
 if (fd<0) return false;
 int scan=openat(fd,".",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
 DIR *directory=scan<0?NULL:fdopendir(scan);
 if (directory==NULL) { if (scan>=0) close(scan); close(fd); return false; }
 bool ok=true;
 for (;;) {
  errno=0; struct dirent *entry=readdir(directory);
  if (entry==NULL) { if (errno!=0) ok=false; break; }
  if (dot(entry->d_name)) continue;
  struct stat slot,target,payload;
  if (fstatat(fd,entry->d_name,&slot,AT_SYMLINK_NOFOLLOW)!=0) { ok=false; break; }
  if (strcmp(entry->d_name,".worldline-generation.json")==0) {
   int marker=openat(fd,entry->d_name,O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK);
   if (marker<0) { ok=false; break; }
   ok=durable_file(marker); int saved=errno; close(marker); errno=saved;
   if (!ok) break;
  } else if (!S_ISLNK(slot.st_mode) ||
     fstatat(fd,entry->d_name,&target,0)!=0 || !S_ISDIR(target.st_mode) ||
     fstatat(payload_fd,entry->d_name,&payload,AT_SYMLINK_NOFOLLOW)!=0 ||
     !S_ISDIR(payload.st_mode) || target.st_dev!=payload.st_dev || target.st_ino!=payload.st_ino) {
   ok=false; break;
  }
 }
 int saved=errno; closedir(directory); errno=saved;
 /* Reverse membership prevents an omitted payload root. Empty rosters stay
  * legal; their admissibility is decided by the full native frame. */
 if (ok) {
  scan=openat(payload_fd,".",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
  directory=scan<0?NULL:fdopendir(scan);
  if (directory==NULL) { if (scan>=0) close(scan); ok=false; }
  else {
   for (;;) {
    errno=0; struct dirent *entry=readdir(directory);
    if (entry==NULL) { if (errno!=0) ok=false; break; }
    if (dot(entry->d_name)) continue;
    struct stat slot;
    if (strcmp(entry->d_name,".worldline-generation.json")==0 ||
        fstatat(fd,entry->d_name,&slot,AT_SYMLINK_NOFOLLOW)!=0 || !S_ISLNK(slot.st_mode)) {
     ok=false; break;
    }
   }
   saved=errno; closedir(directory); errno=saved;
  }
 }
 ok=ok && durable_tree(payload_fd) && fsync(fd)==0;
 saved=errno; close(fd); errno=saved;
 return ok;
}
static bool durable_parent(int fd) {
 int parent=openat(fd,"..",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
 if (parent<0) return false;
 struct stat before,after;
 bool ok=fstat(parent,&before)==0 && S_ISDIR(before.st_mode) &&
  before.st_uid==0 && (before.st_mode&0077)==0 && fsync(parent)==0 &&
  fstat(parent,&after)==0 && stable(&before,&after);
 int saved=errno; close(parent); errno=saved;
 return ok;
}
struct frame {
 const wl_canonical_exchange_input_v1 *input;
 const void *arena; size_t arena_length;
 const void *grants; size_t grant_count,grant_length;
 const void *uses; size_t use_count,use_length;
 const void *rows; size_t row_count,row_length;
 const void *observed; size_t observed_count,observed_length;
 const void *worker_receipts; size_t worker_receipt_count,worker_receipt_length;
 const void *worker_events; size_t worker_event_count,worker_event_length;
 const void *effect_receipts; size_t effect_receipt_count,effect_receipt_length;
 const void *effect_events; size_t effect_event_count,effect_event_length;
 uint8_t required;
};
static bool redecide(void *context) {
 const struct frame *f=context; wl_canonical_exchange_result_v1 result;
 return wl_canonical_exchange_decide_v1(f->input,sizeof(*f->input),f->arena,f->arena_length,
  f->grants,f->grant_count,f->grant_length,f->uses,f->use_count,f->use_length,
  f->rows,f->row_count,f->row_length,f->observed,f->observed_count,f->observed_length,
  f->worker_receipts,f->worker_receipt_count,f->worker_receipt_length,
  f->worker_events,f->worker_event_count,f->worker_event_length,
  f->effect_receipts,f->effect_receipt_count,f->effect_receipt_length,
  f->effect_events,f->effect_event_count,f->effect_event_length,&result,sizeof(result))==0 &&
  result.disposition==f->required;
}
/* Numeric extents/disjointness only. Readability and lifetime are supplied
 * by the actual owned caller, not established by this predicate. */
static bool disjoint_output(const void *output,size_t output_length,
                            const void *input,size_t input_length) {
 uintptr_t a=(uintptr_t)output,b=(uintptr_t)input;
 if (output==NULL || output_length>UINTPTR_MAX-a) return false;
 if (input_length==0) return true;
 if (input==NULL || input_length>UINTPTR_MAX-b) return false;
 return a>=b?input_length<=a-b:output_length<=b-a;
}
static int full_physical(bool recovering,int original_peer_fd,int data_fd,int transaction_fd,int payload_fd,
 const void *input,size_t input_length,const void *arena,size_t arena_length,
 const void *grants,size_t grant_count,size_t grant_length,
 const void *uses,size_t use_count,size_t use_length,
 const void *rows,size_t row_count,size_t row_length,
 const void *observed,size_t observed_count,size_t observed_length,
 const void *worker_receipts,size_t worker_receipt_count,size_t worker_receipt_length,
 const void *worker_events,size_t worker_event_count,size_t worker_event_length,
 const void *effect_receipts,size_t effect_receipt_count,size_t effect_receipt_length,
 const void *effect_events,size_t effect_event_count,size_t effect_event_length,
 const struct wl_actuation_request *actuation,size_t actuation_length,
 struct wl_actuator_witness *witness,size_t witness_length) {
 struct stat data,transaction,payload;
 if (geteuid()!=0 || input==NULL || actuation==NULL || witness==NULL ||
     input_length!=sizeof(wl_canonical_exchange_input_v1) ||
     actuation_length!=sizeof(*actuation) || witness_length!=sizeof(*witness) ||
     fstat(data_fd,&data)!=0 || fstat(transaction_fd,&transaction)!=0 || fstat(payload_fd,&payload)!=0 ||
     !S_ISDIR(data.st_mode) || !S_ISDIR(transaction.st_mode) || !S_ISDIR(payload.st_mode) ||
     data.st_uid!=0 || transaction.st_uid!=0 || payload.st_uid!=0 ||
     (data.st_mode&0077)!=0 || (transaction.st_mode&0077)!=0 || (payload.st_mode&0077)!=0 ||
     (data.st_dev==transaction.st_dev && data.st_ino==transaction.st_ino)) return WL_ACTUATOR_REFUSED;
 if (!disjoint_output(witness,witness_length,input,input_length) ||
     !disjoint_output(witness,witness_length,arena,arena_length) ||
     !disjoint_output(witness,witness_length,grants,grant_length) ||
     !disjoint_output(witness,witness_length,uses,use_length) ||
     !disjoint_output(witness,witness_length,rows,row_length) ||
     !disjoint_output(witness,witness_length,observed,observed_length) ||
     !disjoint_output(witness,witness_length,worker_receipts,worker_receipt_length) ||
     !disjoint_output(witness,witness_length,worker_events,worker_event_length) ||
     !disjoint_output(witness,witness_length,effect_receipts,effect_receipt_length) ||
     !disjoint_output(witness,witness_length,effect_events,effect_event_length) ||
     !disjoint_output(witness,witness_length,actuation,actuation_length)) return WL_ACTUATOR_REFUSED;
 wl_canonical_exchange_input_v1 selected; struct wl_actuation_request physical;
 memcpy(&selected,input,sizeof(selected)); memcpy(&physical,actuation,sizeof(physical));
 if (!recovering) {
  struct ucred peer; socklen_t length=sizeof(peer);
  if (getsockopt(original_peer_fd,SOL_SOCKET,SO_PEERCRED,&peer,&length)!=0 || length!=sizeof(peer) ||
      selected.operation_input.peer.present!=1 || selected.operation_input.peer.value!=peer.uid ||
      selected.operation_input.authority.bound.peer.present!=1 ||
      selected.operation_input.authority.bound.peer.value!=peer.uid) return WL_ACTUATOR_REFUSED;
 }
 if (physical.payload_durable>1 || physical.recovery_clean>1 ||
     memcmp(&physical.collapse_facts,&selected.operation_input.collapse,sizeof(physical.collapse_facts))!=0)
  return WL_ACTUATOR_REFUSED;
 struct frame f={&selected,arena,arena_length,grants,grant_count,grant_length,uses,use_count,use_length,
  rows,row_count,row_length,observed,observed_count,observed_length,
  worker_receipts,worker_receipt_count,worker_receipt_length,worker_events,worker_event_count,worker_event_length,
  effect_receipts,effect_receipt_count,effect_receipt_length,effect_events,effect_event_count,effect_event_length,
  recovering?WL_FULL_RECORD_EFFECT:WL_FULL_DISPATCH_CANONICAL};
 /* Native authorization precedes even the durability syscalls. Recovery uses
  * historical RECORD_EFFECT; it neither substitutes fresh policy nor dispatches. */
 if (!redecide(&f)) return WL_ACTUATOR_REFUSED;
 physical.payload_durable=0; physical.recovery_clean=0;
 struct wl_actuator_witness result; memset(&result,0,sizeof(result));
 result.decision=WL_ACTUATION_INVALID_REQUEST;
 if (!durable_mapping(recovering?data_fd:transaction_fd,recovering?"live":"mapping",payload_fd) ||
     fsync(payload_fd)!=0 || !durable_parent(payload_fd) ||
     !durable_parent(transaction_fd)) {
  result.syscall_errno=errno; memcpy(witness,&result,sizeof(result));
  return recovering?WL_ACTUATOR_POST_EXCHANGE_UNCERTAIN:WL_ACTUATOR_IO_REFUSED;
 }
 physical.payload_durable=1;
 physical.recovery_clean=redecide(&f)?1:0;
 int status=recovering?wl_actuator_recover(data_fd,transaction_fd,&physical,redecide,&f,&result):
                       wl_actuator_exchange(data_fd,transaction_fd,&physical,redecide,&f,&result);
 memcpy(witness,&result,sizeof(result));
 return status;
}
int wl_internal_full_physical_exchange_v1(int original_peer_fd,int data_fd,int transaction_fd,int payload_fd,
 const void *input,size_t input_length,const void *arena,size_t arena_length,
 const void *grants,size_t grant_count,size_t grant_length,
 const void *uses,size_t use_count,size_t use_length,
 const void *rows,size_t row_count,size_t row_length,
 const void *observed,size_t observed_count,size_t observed_length,
 const void *worker_receipts,size_t worker_receipt_count,size_t worker_receipt_length,
 const void *worker_events,size_t worker_event_count,size_t worker_event_length,
 const void *effect_receipts,size_t effect_receipt_count,size_t effect_receipt_length,
 const void *effect_events,size_t effect_event_count,size_t effect_event_length,
 const struct wl_actuation_request *actuation,size_t actuation_length,
 struct wl_actuator_witness *witness,size_t witness_length) {
 return full_physical(false,original_peer_fd,data_fd,transaction_fd,payload_fd,input,input_length,arena,arena_length,grants,grant_count,grant_length,uses,use_count,use_length,rows,row_count,row_length,observed,observed_count,observed_length,worker_receipts,worker_receipt_count,worker_receipt_length,worker_events,worker_event_count,worker_event_length,effect_receipts,effect_receipt_count,effect_receipt_length,effect_events,effect_event_count,effect_event_length,actuation,actuation_length,witness,witness_length);
}

int wl_internal_full_physical_recover_v1(int original_peer_fd,int data_fd,int transaction_fd,int payload_fd,
 const void *input,size_t input_length,const void *arena,size_t arena_length,
 const void *grants,size_t grant_count,size_t grant_length,
 const void *uses,size_t use_count,size_t use_length,
 const void *rows,size_t row_count,size_t row_length,
 const void *observed,size_t observed_count,size_t observed_length,
 const void *worker_receipts,size_t worker_receipt_count,size_t worker_receipt_length,
 const void *worker_events,size_t worker_event_count,size_t worker_event_length,
 const void *effect_receipts,size_t effect_receipt_count,size_t effect_receipt_length,
 const void *effect_events,size_t effect_event_count,size_t effect_event_length,
 const struct wl_actuation_request *actuation,size_t actuation_length,
 struct wl_actuator_witness *witness,size_t witness_length) {
 return full_physical(true,original_peer_fd,data_fd,transaction_fd,payload_fd,input,input_length,arena,arena_length,grants,grant_count,grant_length,uses,use_count,use_length,rows,row_count,row_length,observed,observed_count,observed_length,worker_receipts,worker_receipt_count,worker_receipt_length,worker_events,worker_event_count,worker_event_length,effect_receipts,effect_receipt_count,effect_receipt_length,effect_events,effect_event_count,effect_event_length,actuation,actuation_length,witness,witness_length);
}
