#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <ctype.h>
#include <sched.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>


#define Num_Thread_Names 21 //The number of lookup tables I have

typedef struct {
    const char* thread_lookup1;
    const char* thread_lookup2;
    cpu_set_t cpu_affinity; 
} affinity_struct;

affinity_struct affinity_lookup[Num_Thread_Names];

void define_affinity_lookup() {
    // Render, Game, and RHIThread pinned to Core 8
    CPU_ZERO(&affinity_lookup[0].cpu_affinity);
    CPU_SET(8, &affinity_lookup[0].cpu_affinity);
    affinity_lookup[0].thread_lookup1 = "RenderThread";
    affinity_lookup[0].thread_lookup2 = NULL;

    CPU_ZERO(&affinity_lookup[1].cpu_affinity);
    CPU_SET(8, &affinity_lookup[1].cpu_affinity);
    affinity_lookup[1].thread_lookup1 = "RHIThread";
    affinity_lookup[1].thread_lookup2 = NULL;

    CPU_ZERO(&affinity_lookup[2].cpu_affinity);
    CPU_SET(8, &affinity_lookup[2].cpu_affinity);
    affinity_lookup[2].thread_lookup1 = "GameThread";
    affinity_lookup[2].thread_lookup2 = NULL;

    // Foregworker #0 and #1 pinned to Core 7
    CPU_ZERO(&affinity_lookup[3].cpu_affinity);
    CPU_SET(7, &affinity_lookup[3].cpu_affinity);
    affinity_lookup[3].thread_lookup1 = "Foregro";
    affinity_lookup[3].thread_lookup2 = "0";

    CPU_ZERO(&affinity_lookup[4].cpu_affinity);
    CPU_SET(7, &affinity_lookup[4].cpu_affinity);
    affinity_lookup[4].thread_lookup1 = "Foregro";
    affinity_lookup[4].thread_lookup2 = "1";

    // Backgro-rker #2 and #3 pinned to Core 6
    CPU_ZERO(&affinity_lookup[5].cpu_affinity);
    CPU_SET(6, &affinity_lookup[5].cpu_affinity);
    affinity_lookup[5].thread_lookup1 = "Backgro";
    affinity_lookup[5].thread_lookup2 = "2";

    CPU_ZERO(&affinity_lookup[6].cpu_affinity);
    CPU_SET(6, &affinity_lookup[6].cpu_affinity);
    affinity_lookup[6].thread_lookup1 = "Backgro";
    affinity_lookup[6].thread_lookup2 = "3";

    // Jit thread pool, mali compiler, app process pinned to Core 5
    CPU_ZERO(&affinity_lookup[7].cpu_affinity);
    CPU_SET(5, &affinity_lookup[7].cpu_affinity);
    affinity_lookup[7].thread_lookup1 = "Jit thread pool";
    affinity_lookup[7].thread_lookup2 = NULL;

    CPU_ZERO(&affinity_lookup[8].cpu_affinity);
    CPU_SET(5, &affinity_lookup[8].cpu_affinity);
    affinity_lookup[8].thread_lookup1 = "mali";
    affinity_lookup[8].thread_lookup2 = "compiler";

    CPU_ZERO(&affinity_lookup[9].cpu_affinity);
    CPU_SET(5, &affinity_lookup[9].cpu_affinity);
    affinity_lookup[9].thread_lookup1 = "com.YourCompany.SunTemple2";
    affinity_lookup[9].thread_lookup2 = NULL;

    // Backgro Pool #1 and profiling threads pinned to Core 4
    CPU_ZERO(&affinity_lookup[10].cpu_affinity);
    CPU_SET(4, &affinity_lookup[10].cpu_affinity);
    affinity_lookup[10].thread_lookup1 = "Backgro";
    affinity_lookup[10].thread_lookup2 = "Pool #1";

    CPU_ZERO(&affinity_lookup[11].cpu_affinity);
    CPU_SET(4, &affinity_lookup[11].cpu_affinity);
    affinity_lookup[11].thread_lookup1 = "AudioMi";
    affinity_lookup[11].thread_lookup2 = "nder(1)";

    CPU_ZERO(&affinity_lookup[12].cpu_affinity);
    CPU_SET(4, &affinity_lookup[12].cpu_affinity);
    affinity_lookup[12].thread_lookup1 = "AudioTrack";
    affinity_lookup[12].thread_lookup2 = NULL;

    CPU_ZERO(&affinity_lookup[13].cpu_affinity);
    CPU_SET(4, &affinity_lookup[13].cpu_affinity);
    affinity_lookup[13].thread_lookup1 = "malieventhand";
    affinity_lookup[13].thread_lookup2 = NULL;

    CPU_ZERO(&affinity_lookup[14].cpu_affinity);
    CPU_SET(4, &affinity_lookup[14].cpu_affinity);
    affinity_lookup[14].thread_lookup1 = "FAsyncLoading";
    affinity_lookup[14].thread_lookup2 = NULL;

    // Binder threads — check logic with "contains" — pinned to Core 3
    CPU_ZERO(&affinity_lookup[15].cpu_affinity);
    CPU_SET(3, &affinity_lookup[15].cpu_affinity);
    affinity_lookup[15].thread_lookup1 = "binder";
    affinity_lookup[15].thread_lookup2 = NULL;

    // Misc system threads pinned to Core 2
    CPU_ZERO(&affinity_lookup[16].cpu_affinity);
    CPU_SET(2, &affinity_lookup[16].cpu_affinity);
    affinity_lookup[16].thread_lookup1 = "InsetsAnimation";
    affinity_lookup[16].thread_lookup2 = NULL;

    CPU_ZERO(&affinity_lookup[17].cpu_affinity);
    CPU_SET(2, &affinity_lookup[17].cpu_affinity);
    affinity_lookup[17].thread_lookup1 = "GoogleApiHandle";
    affinity_lookup[17].thread_lookup2 = NULL;

    CPU_ZERO(&affinity_lookup[18].cpu_affinity);
    CPU_SET(2, &affinity_lookup[18].cpu_affinity);
    affinity_lookup[18].thread_lookup1 = "HeapTaskDaemon";
    affinity_lookup[18].thread_lookup2 = NULL;

    CPU_ZERO(&affinity_lookup[19].cpu_affinity);
    CPU_SET(2, &affinity_lookup[19].cpu_affinity);
    affinity_lookup[19].thread_lookup1 = "RTHeartBeat 0";
    affinity_lookup[19].thread_lookup2 = NULL;

    CPU_ZERO(&affinity_lookup[20].cpu_affinity);
    CPU_SET(2, &affinity_lookup[20].cpu_affinity);
    affinity_lookup[20].thread_lookup1 = "IoDispatcher";
    affinity_lookup[20].thread_lookup2 = NULL;

    // Default: threads not matched above are pinned to Core 1

    // Tool program itself pinned to Core 0 via taskset
}


//Function to read TIDs and set affinity 
void set_thread_affinity(pid_t pid, char* proc_path, cpu_set_t* default_affinity1, cpu_set_t* default_affinity2, cpu_set_t* default_affinity3, cpu_set_t* core1_affinity) {
    //Open directive with TIDs
    DIR* dir = opendir(proc_path);
    //Error if directive does not open 
    if (!dir) {
        perror("Failed to open task directory");
        return;
    }

    //Read the TID from the name of its directories  
    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        //Only read the directory name (directories are named the TID)
        if (entry->d_type != DT_DIR) continue;

        //Check if the name is all digits to confirm it is a TID
        int is_tid = 1;
        //Iterate through each character - null terminated 
        for (int i = 0; entry->d_name[i] != '\0'; i++) {
            if (!isdigit(entry->d_name[i])) {
                is_tid = 0;
                break;
            }
        }

        if (is_tid) {
            //Convert thread ID string to pid_t type 
            pid_t tid = (pid_t)atoi(entry->d_name);
            //printf("Checking thread TID: %d\n", tid);
            
            //Initialize cpu_set_t affinity 
            cpu_set_t affinity;
            CPU_ZERO(&affinity);


            if (sched_getaffinity(tid, sizeof(cpu_set_t), &affinity) == -1) {
                perror("reading current affinity failed");
                continue;
            }
            
            //printf("Comparing affinities for TID %d\n", tid);
            //printf("  Current affinity mask: %lx\n", *(unsigned long *)&affinity);

            //Check if affinity has already been updated 
            int affinity_is_default = CPU_EQUAL(&affinity, default_affinity1) || CPU_EQUAL(&affinity, default_affinity2) || CPU_EQUAL(&affinity, default_affinity3);

            //printf("  CPU_EQUAL result: %d\n", affinity_is_default);


            //If affinity is still 1ff need to pin to core 
            if (affinity_is_default){
                char TID_name_path[256];
                //Hold path to TID_directory/comm in TID_path 
                snprintf(TID_name_path, sizeof(TID_name_path), "/proc/%d/task/%s/comm", pid, entry->d_name);

                //Read comm file containing thread name 
                FILE* comm_file = fopen(TID_name_path, "r");
                if (comm_file){
                    //initalzie thread name variable
                    char thread_name[64];
                    //Initialize affinty_set variable
                    int affinity_set;
                    //Store thread name 
                    if (fgets(thread_name, sizeof(thread_name), comm_file)){
                        //Replace new line (\n) with null terminator 
                        thread_name[strcspn(thread_name, "\n")] = 0; 
                        //printf("Thread name: '%s'\n", thread_name);

                        printf("Thread name seen: '%s'\n", thread_name);

                        //Display the Thread ID Name and Affinity Mask 
                        //printf("Thread TID: %d, Name: '%s', Current affinity mask: %lx\n",
                        //tid, thread_name, *(unsigned long *)&affinity);

                        //Pin thread based on name 
                        
                        //Initalize varaible to declare we have set affinity 
                        affinity_set = 0;

                        //Cycle through each element in the lookup array
                        for (int i = 0; i < Num_Thread_Names; i++){
                            if (strstr(thread_name, affinity_lookup[i].thread_lookup1) && (affinity_lookup[i].thread_lookup2 == NULL || strstr(thread_name, affinity_lookup[i].thread_lookup2))) {
                                affinity_set = 1;
                                //Set affinity for matching name 
                                if (sched_setaffinity(tid, sizeof(cpu_set_t), &affinity_lookup[i].cpu_affinity) == -1){
                                    perror("sched_setaffinity failed");
                                } else {
                                    printf("Pinned thread '%s' (TID %d) for string '%s'\n", thread_name, tid, affinity_lookup[i].thread_lookup1);
                                }
                                break; //Stop checking once affinity set 
                            }
                        }
                    }

                    //If affinity was not set - set to core 1 
                    if (!affinity_set){
                        if (sched_setaffinity(tid, sizeof(cpu_set_t), core1_affinity) == -1) {
                            perror("sched_setaffinity default failed");
                        } else {
                            printf("Pinned thread '%s' (TID %d) to default CPU 1\n", thread_name, tid);
                        }
                    }

                    fclose(comm_file);
                } else {
                    perror("Failed to open comm file");
                }
            }

        }
    }
    closedir(dir);
}


int main (int argc, char* argv[]){
    //Collect pid passed through command line 
    pid_t pid = (pid_t)atoi(argv[1]);
    //Collect poll rate in ms from command line 
    int poll_rate = atoi(argv[2]);

    //Disable buffering on stdout - allows us to see printf messages in the command line 
    setbuf(stdout, NULL);

    printf("Daemon starting with PID: %d, poll interval: %d ms\n", pid, poll_rate);

    define_affinity_lookup();

    //Initialize char holding the path to TID data
    char proc_path[256];
    snprintf(proc_path, sizeof(proc_path), "/proc/%d/task", pid);

    //Set variable for default affinities
    //1ff
    cpu_set_t default_affinity1;
    CPU_ZERO(&default_affinity1);
    for (int i = 0; i <= 8; i++) {
        CPU_SET(i, &default_affinity1);
    } 
    //printf("Default affinity mask 1: %lx\n", *(unsigned long *)&default_affinity1);

    //1f0
    cpu_set_t default_affinity2;
    CPU_ZERO(&default_affinity2);
    for (int i = 4; i <= 8; i++) {
            CPU_SET(i, &default_affinity2);  
    }
    //printf("Default affinity1 mask 2: %lx\n", *(unsigned long *)&default_affinity2);

    //f
    cpu_set_t default_affinity3;
    CPU_ZERO(&default_affinity3);
    for (int i = 0; i <= 3; i++) {
            CPU_SET(i, &default_affinity3);  
    }
    //printf("Default affinity1 mask 3: %lx\n", *(unsigned long *)&default_affinity3);

    //Set variable for core 1 affinity
    cpu_set_t core1_affinity; 
    CPU_ZERO(&core1_affinity);
    CPU_SET(1, &core1_affinity);
    //printf("Core 1 affinity mask: %lx\n", *(unsigned long *)&core1_affinity);

    while (1) {
        set_thread_affinity(pid, proc_path, &default_affinity1, &default_affinity2, &default_affinity3, &core1_affinity);
        usleep(poll_rate * 1000);
    }
}