#include "kernel/types.h"
#include "user.h"

#define MAP_SIZE 4096

int main(int argc, char *argv[]) {
    int disable_unmap = 0;
    if (argc > 1 && (strcmp(argv[1], "-n") == 0 || strcmp(argv[1], "--no-unmap") == 0)) {
        disable_unmap = 1;
    }

    char *buf = malloc(MAP_SIZE);
    int p[2];
    pipe(p);

    int pid = fork();

    if (pid < 0) {
        exit(1);
    }

    if (pid == 0) {
        // Child process
        close(p[1]);
        uint64 shared_addr;
        printf("Child process size before mapping: %d bytes\n", sbrk(0));
        read(p[0], &shared_addr, sizeof(shared_addr));
        close(p[0]);
        printf("Child process size after mapping: %d bytes\n", sbrk(0));

        strcpy((char*)shared_addr, "Hello daddy"); // Write to shared memory

        if (!disable_unmap) {
            if (unmap_shared_pages(shared_addr, MAP_SIZE) == 0) {
                printf("Child process size after unmapping: %d bytes\n", sbrk(0));
            } else {
                printf("Child failed to unmap shared memory\n");
            }
        } else {
            printf("Child did not unmap shared memory (flag set)\n");
        }

        // malloc after (un)map
        
        malloc(61440);
        printf("Child process size after malloc: %d bytes\n", sbrk(0));
        

        exit(0);
    } else {
        // Parent process
        close(p[0]);
        uint64 shared_addr = map_shared_pages((uint64)buf, MAP_SIZE, pid);
        write(p[1], &shared_addr, sizeof(shared_addr));
        close(p[1]);

        sleep(2); // Give child time to write

        printf("Parent reads: %s\n", buf);

        wait(0);

        // After child exit, see if the parent can still read the shared buffer
        printf("Parent reads after child exit: %s\n", buf);

        exit(0);
    }
}
