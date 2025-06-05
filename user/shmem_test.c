#include "kernel/types.h"
#include "user.h"

#define MAP_SIZE 2048

int main() {
    char *buf = malloc(MAP_SIZE);
    int pid = fork();

    if(pid < 0) {
        exit(1);
    }
    if(pid == 0) {
    // Child process
    printf("Child: Process size = %d bytes\n", sbrk(0));
    sleep(2);
    printf("Child: Process size = %d bytes\n", sbrk(0));
    if(-1==unmap_shared_pages((uint64)buf, MAP_SIZE)){
        printf("Child: Failed to unmap shared pages\n");
    }
    else{
        printf("Child: Shared memory unmapped successfully\n");
    }
    printf("Child: Process size = %d bytes\n", sbrk(0));
    // malloc(MAP_SIZE);
    // printf("Child: Process size = %d bytes\n", sbrk(0));
    exit(0);
} else {
    // Parent process
    sleep(1);
    // printf("Parent: Child PID = %d\n", pid);
    // printf("Parent: Setting up shared memory\n");
    if(map_shared_pages((uint64)buf, MAP_SIZE, pid)==-1){
        printf("Parent: Failed to map shared pages\n");
    }
    else{
        printf("Parent: Shared memory mapped successfully\n");
    }
    // printf("Parent: Shared memory set up\n");
    // sleep(2);
    // printf("Parent: Reading message: '%s'\n", buf);
    wait(0);
    // printf("Parent: Child finished\n");
    exit(0);
}
}