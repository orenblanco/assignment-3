#include "kernel/types.h"
#include "user.h"

#define NUM_CHILDREN 4
#define BUF_SIZE 4096

int main() {
    int pipes[NUM_CHILDREN][2];
    int child_pids[NUM_CHILDREN];
    char *log_buffer = malloc(BUF_SIZE);

    // Fork children and set up pipes
    for (int i = 0; i < NUM_CHILDREN; i++) {
        pipe(pipes[i]);
        int pid = fork();
        if (pid == 0) {
            // --- Child process ---
            close(pipes[i][1]); // Close write end
            uint64 shared_addr;
            read(pipes[i][0], &shared_addr, sizeof(shared_addr));
            close(pipes[i][0]);

            // Prepare message (simple, no sprintf)
            char msg[1001]; // 1000 characters + '\0'

            for (int i = 0; i < 1000; i++) {
                msg[i] = 'A'; // or any character you like
            }
            msg[1000] = '\0'; // Null-terminate

            int msg_len = strlen(msg);
            // Prepare header value once
            uint32 header_val = (i << 16) | msg_len;
            // Find first available slot using atomic CAS
            uint64 addr = shared_addr;
            int found = 0;
            while (addr + 4 + msg_len < shared_addr + BUF_SIZE) {
                uint32 *header = (uint32*)addr;
                // Atomically claim if header is 0
                if (__sync_val_compare_and_swap(header, 0, header_val) == 0) {
                    strcpy((char *)(addr + 4), msg);
                    found = 1;
                    break;
                }
                // Skip to next slot
                uint16 mlen = (*header) & 0xFFFF;
                addr += 4 + mlen;
                addr = (addr + 3) & ~3;
            }
            if (!found) {
                printf("Child %d: No space in buffer!\n", i);
            }
            exit(0);
        } else if (pid > 0) {
            child_pids[i] = pid;
        } else {
            printf("fork failed\n");
            exit(1);
        }
    }

    // Parent: share buffer with each child and send address
    for (int i = 0; i < NUM_CHILDREN; i++) {
        uint64 shared_addr = map_shared_pages((uint64)log_buffer, BUF_SIZE, child_pids[i]);
        if (shared_addr == (uint64)-1) {
            printf("Parent failed to map buffer to child %d\n", i);
            exit(1);
        }
        close(pipes[i][0]);
        write(pipes[i][1], &shared_addr, sizeof(shared_addr));
        close(pipes[i][1]);
    }

    // Wait for children
    sleep(10);

    // Print the messages from buffer
    printf("\nLog buffer content:\n");
    uint64 addr = (uint64)log_buffer;
    while (addr < (uint64)log_buffer + BUF_SIZE) {
        uint32 *header = (uint32*)addr;
        if (*header == 0) break; // No more messages
        int idx = (*header) >> 16;
        int len = (*header) & 0xFFFF;
        printf("From child %d: %s\n", idx, (char *)(addr + 4));
        addr += 4 + len;
        addr = (addr + 3) & ~3;
    }

    free(log_buffer);
    exit(0);
}
