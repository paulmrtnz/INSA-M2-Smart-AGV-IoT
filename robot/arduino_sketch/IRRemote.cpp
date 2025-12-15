#include "IRRemote.h"

IRRemote::IRRemote(int recvPin) {
    _irrecv = new IRrecv(recvPin);
}

IRRemote::~IRRemote() {
    delete _irrecv;
}

void IRRemote::setup() {
    _irrecv->enableIRIn();
}

unsigned long IRRemote::readCommand() {
    if (_irrecv->decode(&_results)) {
        unsigned long command = _results.value;
        // Return the command value, including 0xFFFFFFFF (repeat code) for continuous button holds
        _irrecv->resume(); // Ready to receive the next command
        return command;
    }
    return 0; // No new command
}
