#include <vector>
#include <iostream>
#include <stdlib.h>
#include <assert.h>
#include <math.h>
#include <fstream>


#define show(s) std::cout << #s " = " << s << std::endl

float rand(float a, float b) {
    float r01 = float(rand()) / float(RAND_MAX);
    return a + r01 * (b - a);
}

struct Client {
    int targetFloor = -1;
    float startTime = -1;
    float endTime   = -1;
};

struct Lift {
    bool movingUp = true;
    std::vector<Client> clients;

    int total() {
        return clients.size();
    }

    int goOutOnFloorCount(int target) {
        int count = 0;
        for (auto client : clients) {
            if (client.targetFloor == target) {
                count++;
            }
        }
        return count;
    }
};

enum TransactType {
    AddClient,
    MoveLift,
    InOut
};

struct Transact {
    TransactType type;

    union {
        struct {
            int from;
            int to;
        } client;
        struct {
            int index;
            int floor;
        } lift;
    } data;

    float startTime;
    float endTime;
};

struct System {
    std::vector<Lift> lifts;

    // queues on floors
    std::vector<std::vector<Client>> queues;
    std::vector<int> floorLiftIndices; // what lift is going to this floor, -1 means None

    std::vector<Transact> transacts;

    float time = 0;

    int k = 10;
    int liftMoveTime = 3;
    int numberOfFloors = 100;
    int numberOfLifts  = 10;
    float endTime = 10000;
    int liftSize = 10;

    int task = 2;

    struct {
        int totalClientsMoved = 0;
    } stats;

    void init() {
        lifts.resize(numberOfLifts);
        queues.resize(numberOfFloors);
        floorLiftIndices.resize(numberOfFloors, -1);
    }

    void addClient(Transact transact) {
        // add client
        Client client;
        client.targetFloor = transact.data.client.to;
        client.startTime   = time;
        queues[transact.data.client.from].push_back(client);

        // generate transact
        Transact newTransact = transact;
        newTransact.startTime = time;
        int target = std::max(transact.data.client.to, transact.data.client.from);
        if (target+1 > k) {
            newTransact.endTime = time + rand(0, 2 * 60. / log2(k));
        } else {
            newTransact.endTime = time + rand(0, 2 * 60. / log2(target + 1));
        }

        transacts.push_back(newTransact);
    }

    void liftArrived(Transact transact) {
        int floor = transact.data.lift.floor;
        assert(floor >= 0);
        int liftIndex = transact.data.lift.index;
        int goOut = lifts[liftIndex].goOutOnFloorCount(floor);
        int liftTotal = lifts[liftIndex].total();
        int goIn  = queues[floor].size();
        if (liftTotal - goOut + goIn > liftSize) {
            goIn = liftSize - (liftTotal - goOut);
        }

        Transact newTransact = transact;
        newTransact.type      = InOut;
        newTransact.startTime = time;
        newTransact.endTime   = time + rand(log2(goOut + goIn + 2), log2(liftTotal + queues[floor].size() + 2));

        // this is task 2 and lift is moving up
        bool ignoreThisFloor = task == 2 && lifts[liftIndex].movingUp && floor != 0 && goOut == 0;

        // this floor is handled by another lift
        ignoreThisFloor = ignoreThisFloor || (goOut == 0 && floorLiftIndices[floor] != -1 && floorLiftIndices[floor] != liftIndex);

        if ((goIn == 0 && goOut == 0) || ignoreThisFloor) {
            newTransact.endTime = time;
        }

        transacts.push_back(newTransact);

        if (ignoreThisFloor) {
            return;
        }

        stats.totalClientsMoved += goOut;

        // people leave lift
        auto& clients = lifts[liftIndex].clients;
        for (int i = 0; i < clients.size(); ++i) {
            if (clients[i].targetFloor == floor) {
                clients.erase(clients.begin() + i);
                i--;
            }
        }

        // peolpe enter lift
        for (int i = 0; i < goIn; ++i) {
            lifts[liftIndex].clients.push_back(queues[floor][i]);
        }
        queues[floor].erase(queues[floor].begin(), queues[floor].begin() + goIn);

        if (floorLiftIndices[floor] == liftIndex) {
            floorLiftIndices[floor] = -1;
        }
    }

    void moveLift(Transact transact) {
        auto& lift = transact.data.lift;
        int floor =     lift.floor;
        int liftIndex = lift.index;

        bool floorAboveFound = false;
        int targetFloor = floor;

        if (floor == 0) {
            lifts[liftIndex].movingUp = true;
        }

        if (lifts[liftIndex].movingUp) {
            // choose target floor
            for (auto client : lifts[liftIndex].clients) {
                if (client.targetFloor > floor) {
                    targetFloor = client.targetFloor;
                    floorAboveFound = true;
                }
            }

            // check floor above
            // if (task != 2) {
                for (int f = floor + 1; f < numberOfFloors; ++f) {
                    if (floorLiftIndices[f] == -1 && queues[f].size()) {
                        floorLiftIndices[f] = liftIndex;
                        floorAboveFound = true;
                        break;
                    }
                }
            // }

            if (floorAboveFound) {
                targetFloor = floor + 1;
            } else if (floor != 0) {
                lifts[liftIndex].movingUp = false;
            }
        }

        if (!lifts[liftIndex].movingUp) {
            // always move down by 1 floor
            targetFloor = floor - 1;
        }

        Transact newTransact;
        newTransact.type = MoveLift;
        newTransact.data.lift.index = transact.data.lift.index;
        newTransact.data.lift.floor = targetFloor;
        newTransact.startTime = time;
        if (targetFloor != floor) {
            newTransact.endTime = time + liftMoveTime * abs(targetFloor - floor);
        } else {
            assert(lifts[liftIndex].clients.empty());
            // wait for next event
            float nextTransactTime = time;
            for (auto& t : transacts) {
                if (t.endTime > time) {
                    nextTransactTime = t.endTime;
                    break;
                }
            }
            newTransact.endTime = time + nextTransactTime;
        }

        transacts.push_back(newTransact);

        assert(newTransact.data.lift.floor >= 0);
        assert(newTransact.data.lift.floor < numberOfFloors);
    }

    void run() {
        // start generating clients
        for (int i = 1; i < queues.size(); ++i) {
            int d = i+1 > k ? k : i;

            Transact newTransact;
            newTransact.type = AddClient;
            newTransact.data.client.from = 0;
            newTransact.data.client.to   = i;
            newTransact.startTime = time;
            newTransact.endTime = time + rand(0, 2 * 60./log2(d+1));

            // add client from 0 to i+1
            transacts.push_back(newTransact);

            // addclient from i to i-1
            newTransact.data.client.from = i;
            newTransact.data.client.to   = i-1;

            transacts.push_back(newTransact);
        }

        // it's dumb
        std::sort(transacts.begin(), transacts.end(), [](Transact a, Transact b){
            return a.endTime < b.endTime;
        });

        // all lifts are waiting for the first transact
        for (int i = 0; i < lifts.size(); ++i) {
            Transact newTransact;
            newTransact.type = MoveLift;
            newTransact.data.lift.floor = 0;
            newTransact.data.lift.index = i;
            newTransact.startTime = time;
            newTransact.endTime   = transacts[0].endTime;

            transacts.push_back(newTransact);
        }

        while (time < endTime) {
            int handled = 0;
            for (auto transact : transacts) {
                if (transact.endTime > time) {
                    break;
                }
                handled++;
                if (transact.type == AddClient) {
                    addClient(transact);
                } else if (transact.type == MoveLift) {
                    liftArrived(transact);
                } else if (transact.type == InOut) {
                    moveLift(transact);
                } else {
                    assert(0);
                }
            }

            transacts.erase(transacts.begin(), transacts.begin() + handled);

            // it's dumb
            std::sort(transacts.begin(), transacts.end(), [](Transact a, Transact b){
                return a.endTime < b.endTime;
            });

            // update time
            time = transacts[0].endTime;
        }

        int k = 1242;
    }
};

int main() {
    std::fstream f;
    f.open("data.txt", std::ios::out);

    System system;
    system.init();
    system.run();
    show(system.stats.totalClientsMoved);
}
