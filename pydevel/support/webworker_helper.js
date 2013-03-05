self.onmessage = function(e) {
    // Reset onmessage to given function
    self.onmessage = null;
    eval('self.onmessage = ' + e.data + ';');
};
