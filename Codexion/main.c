#include <pthread.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/time.h>

int mails = 0;
int lock = 0;

pthread_mutex_t mutex;


void *routine()
{
    int i = 0;
    while(i < 10){
        pthread_mutex_lock(&mutex);
        printf("Thread %ld is sending mail %d\n", pthread_self(), mails);
        mails++;
        pthread_mutex_unlock(&mutex);
        i++;
    }
}

int main(int argc, char **argv)
{
    pthread_t th[4];
    pthread_mutex_init(&mutex, NULL);
    struct timeval start;
    gettimeofday(&start, NULL);
    int i = 0;
    while (i < 4)
    {
        pthread_create(&th[i], NULL, &routine, NULL);
        printf("Thread %d has started\n", i);
        i++;
    }
    i = 0;
    while (i < 4)
    {
        pthread_join(th[i], NULL);
        printf("Thread %d has finished\n", i);
        i++;
    }

    struct timeval end;
    gettimeofday(&end, NULL);
    int mili_seconds = 0;
    mili_seconds = (end.tv_sec - start.tv_sec) * 1000 + (end.tv_usec - start.tv_usec) / 1000;
    printf("Execution time: %d milliseconds\n", mili_seconds);
    printf("Mails: %d\n", mails);
    pthread_mutex_destroy(&mutex);
    return 0;
}