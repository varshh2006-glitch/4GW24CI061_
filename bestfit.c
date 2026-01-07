#include <stdio.h>

int main() {
    int b[5] = {100, 500, 200, 300, 600};
    int p[4] = {212, 417, 112, 426};
    int allocation[4];
    int i, j;

    for (i = 0; i < 4; i++)
        allocation[i] = -1;

    for (i = 0; i < 4; i++) {
        int best = -1;
        for (j = 0; j < 5; j++) {
            if (b[j] >= p[i]) {
                if (best == -1 || b[j] < b[best])
                    best = j;
            }
        }
        if (best != -1) {
            allocation[i] = best;
            b[best] -= p[i];
        }
    }

    printf("Process No\tProcess Size\tBlock No\n");
    for (i = 0; i < 4; i++) {
        printf("%d\t\t%d\t\t", i+1, p[i]);
        if (allocation[i] != -1)
            printf("%d\n", allocation[i]+1);
        else
            printf("Not Allocated\n");
    }

    return 0;
}
