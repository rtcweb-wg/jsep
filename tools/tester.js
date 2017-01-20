function canonicalize(sdp) {
    let lines = sdp.split("\n");
    let output = "";
        
    for (l in lines) {
        let trimmed = lines[l].trim()
        if (lines[l].length === 0) {
            continue;
        }
        if (lines[l].startsWith(' ')) {
            // Line folding
            if (!trimmed.startsWith(':')) {
                output += ' ';
            }
        } else if (output.length > 0) {
            // No line folding and not first line.
            output += "\n";
        }
        output += trimmed;
    }
    return output + "\n";
}

function test() {
    let sdp = document.getElementById("offer").value;
    console.log("Original SDP" + sdp);
    let canon = canonicalize(sdp);
    
    console.log("Canonical SDP:" + canon);
    
    let pc = new RTCPeerConnection();
    pc.setRemoteDescription(
        {
            type : "offer",
            sdp : canon
        },
        function () {
            alert("Success");
        },
        function (e) {
            alert("Error "+e);
        });
}



