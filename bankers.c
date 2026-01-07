#include <stdio.h>

int main() {
    int n = 5, m = 3;   // n = processes, m = resources

    int alloc[5][3] = {
        {2, 0, 0},
        {3, 1, 4},
        {2, 0, 1},
        {2, 3, 4},
        {1, 1, 1}
    };

    int max[5][3] = {
        {8, 2, 6},
        {4, 6, 1},
        {9, 3, 1},
        {1, 1, 1},
        {5, 6, 7}
    };

    int avail[3] = {3, 2, 2};

    int need[5][3];
    int finish[5] = {0}, safeSeq[5];
    int i, j, k;

    // Calculate NEED matrix
    for (i = 0; i < n; i++)
        for (j = 0; j < m; j++)
            need[i][j] = max[i][j] - alloc[i][j];

    int count = 0;
    while (count < n) {
        int found = 0;

        for (i = 0; i < n; i++) {
            if (finish[i] == 0) {
                for (j = 0; j < m; j++)
                    if (need[i][j] > avail[j])
                        break;

                if (j == m) {
                    for (k = 0; k < m; k++)
                        avail[k] += alloc[i][k];

                    safeSeq[count++] = i;
                    finish[i] = 1;
                    found = 1;
                }
            }
        }

        if (!found) {
            printf("System is not in safe state\n");
            return 0;
        }
    }

    printf("System is in safe state\nSafe sequence: ");
    for (i = 0; i < n; i++)
        printf("P%d ", safeSeq[i]);

    return 0;
}
