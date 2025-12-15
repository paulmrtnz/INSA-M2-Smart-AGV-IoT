#ifndef IR_REMOTE_H
#define IR_REMOTE_H

#include <IRremote.h>

class IRRemote {
public:
    explicit IRRemote(int recvPin);
    ~IRRemote();

    void setup();
    unsigned long readCommand();

private:
    IRrecv* _irrecv;
    decode_results _results;
};

#endif // IR_REMOTE_H
