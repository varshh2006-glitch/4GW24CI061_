#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

int main()
{
    pid_t pid;
    pid = fork();   // create process

    if (pid < 0)
    {
        printf("Fork failed\n");
    }
    else if (pid == 0)
    {
        printf("Child Process\n");
        execlp("/bin/ls", "ls", NULL);   // execute command
    }
    else
    {
        wait(NULL);   // wait for child
        printf("Parent Process: Child terminated\n");
    }
    return 0;
}