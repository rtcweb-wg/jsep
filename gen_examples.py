offer_a1 = """
  v=0
  o=- 4962303333179871722 1 IN IP4 0.0.0.0
  s=-
  t=0 0
  a=group:BUNDLE a1 v1
  a=ice-options:trickle
  m=audio 56500 UDP/TLS/RTP/SAVPF 96 0 8 97 98
  c=IN IP4 192.0.2.1
  a=mid:a1
  a=rtcp:56501 IN IP4 192.0.2.1
  a=msid:47017fee-b6c1-4162-929c-a25110252400
         f83006c5-a0ff-4e0a-9ed9-d3e6747be7d9
  a=sendrecv
  a=rtpmap:96 opus/48000/2
  a=rtpmap:0 PCMU/8000
  a=rtpmap:8 PCMA/8000
  a=rtpmap:97 telephone-event/8000
  a=rtpmap:98 telephone-event/48000
  a=maxptime:120
  a=ice-ufrag:ETEn1v9DoTMB9J4r
  a=ice-pwd:OtSK0WpNtpUjkY4+86js7ZQl
  a=fingerprint:sha-256
                19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04
               :BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2
  a=setup:actpass
  a=rtcp-mux
  a=rtcp-rsize
  a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
  a=extmap:2 urn:ietf:params:rtp-hdrext:sdes:mid
  a=candidate:3348148302 1 udp 2113937151 192.0.2.1 56500
              typ host
  a=candidate:3348148302 2 udp 2113937151 192.0.2.1 56501
              typ host
  a=end-of-candidates

  m=video 56502 UDP/TLS/RTP/SAVPF 100 101
  c=IN IP4 192.0.2.1
  a=rtcp:56503 IN IP4 192.0.2.1
  a=mid:v1
  a=msid:61317484-2ed4-49d7-9eb7-1414322a7aae
         f30bdb4a-5db8-49b5-bcdc-e0c9a23172e0
  a=sendrecv
  a=rtpmap:100 VP8/90000
  a=rtpmap:101 rtx/90000
  a=fmtp:101 apt=100
  a=ice-ufrag:BGKkWnG5GmiUpdIV
  a=ice-pwd:mqyWsAjvtKwTGnvhPztQ9mIf
  a=fingerprint:sha-256
                19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04
               :BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2
  a=setup:actpass
  a=rtcp-mux
  a=rtcp-rsize
  a=extmap:3 urn:ietf:params:rtp-hdrext:sdes:mid
  a=rtcp-fb:100 ccm fir
  a=rtcp-fb:100 nack
  a=rtcp-fb:100 nack pli
  a=candidate:3348148302 1 udp 2113937151 192.0.2.1 56502
              typ host
  a=candidate:3348148302 2 udp 2113937151 192.0.2.1 56503
              typ host
  a=end-of-candidates
"""

answer_a1 =
"""
  v=0
  o=- 6729291447651054566 1 IN IP4 0.0.0.0
  s=-
  t=0 0
  a=group:BUNDLE a1 v1
  m=audio 20000 UDP/TLS/RTP/SAVPF 96 0 8 97 98
  c=IN IP4 192.0.2.2
  a=mid:a1
  a=rtcp:20000 IN IP4 192.0.2.2
  a=msid:PI39StLS8W7ZbQl1sJsWUXkr3Zf12fJUvzQ1
         PI39StLS8W7ZbQl1sJsWUXkr3Zf12fJUvzQ1a0
  a=sendrecv
  a=rtpmap:96 opus/48000/2
  a=rtpmap:0 PCMU/8000
  a=rtpmap:8 PCMA/8000
  a=rtpmap:97 telephone-event/8000
  a=rtpmap:98 telephone-event/48000
  a=maxptime:120
  a=ice-ufrag:6sFvz2gdLkEwjZEr
  a=ice-pwd:cOTZKZNVlO9RSGsEGM63JXT2
  a=fingerprint:sha-256 6B:8B:F0:65:5F:78:E2:51:3B:AC:6F:F3:3F:46:1B:35
              :DC:B8:5F:64:1A:24:C2:43:F0:A1:58:D0:A1:2C:19:08
  a=setup:active
  a=rtcp-mux
  a=rtcp-rsize
  a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
  a=candidate:2299743422 1 udp 2113937151 192.0.2.2 20000
              typ host
  a=end-of-candidates

  m=video 20000 UDP/TLS/RTP/SAVPF 100 101
  c=IN IP4 192.0.2.2
  a=rtcp 20001 IN IP4 192.0.2.2
  a=mid:v1
  a=msid:PI39StLS8W7ZbQl1sJsWUXkr3Zf12fJUvzQ1
         PI39StLS8W7ZbQl1sJsWUXkr3Zf12fJUvzQ1v0
  a=sendrecv
  a=rtpmap:100 VP8/90000
  a=rtpmap:101 rtx/90000
  a=fmtp:101 apt=100
  a=fingerprint:sha-256 6B:8B:F0:65:5F:78:E2:51:3B:AC:6F:F3:3F:46:1B:35
                       :DC:B8:5F:64:1A:24:C2:43:F0:A1:58:D0:A1:2C:19:08
  a=setup:active
  a=rtcp-mux
  a=rtcp-rsize
  a=rtcp-fb:100 ccm fir
  a=rtcp-fb:100 nack
  a=rtcp-fb:100 nack pli
"""

offer_b1 = """
  v=0
  o=- 4962303333179871723 1 IN IP4 0.0.0.0
  s=-
  t=0 0
  a=group:BUNDLE a1 d1
  a=ice-options:trickle
  m=audio 9 UDP/TLS/RTP/SAVPF 96 0 8 97 98
  c=IN IP4 0.0.0.0
  a=rtcp:9 IN IP4 0.0.0.0
  a=mid:a1
  a=msid:57017fee-b6c1-4162-929c-a25110252400
         e83006c5-a0ff-4e0a-9ed9-d3e6747be7d9
  a=sendrecv
  a=rtpmap:96 opus/48000/2
  a=rtpmap:0 PCMU/8000
  a=rtpmap:8 PCMA/8000
  a=rtpmap:97 telephone-event/8000
  a=rtpmap:98 telephone-event/48000
  a=maxptime:120
  a=ice-ufrag:ATEn1v9DoTMB9J4r
  a=ice-pwd:AtSK0WpNtpUjkY4+86js7ZQl
  a=fingerprint:sha-256
                19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04
               :BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2
  a=setup:actpass
  a=rtcp-mux
  a=rtcp-rsize
  a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
  a=extmap:2 urn:ietf:params:rtp-hdrext:sdes:mid

  m=application 0 UDP/DTLS/SCTP webrtc-datachannel
  c=IN IP4 0.0.0.0
  a=bundle-only
  a=mid:d1
  a=fmtp:webrtc-datachannel max-message-size=65536
  a=sctp-port 5000
  a=fingerprint:sha-256 19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04
                       :BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2
  a=setup:actpass
"""

candidate_b1 = """
  candidate:109270923 1 udp 2122194687 192.168.1.2 51556 typ host
"""

candidate_b2 = """
  candidate:4036177503 1 udp 1685987071 11.22.33.44 52546 typ srflx
            raddr 192.168.1.2 rport 51556
"""

answer_b1 = """
o=- 7729291447651054566 1 IN IP4 0.0.0.0
s=-
t=0 0
a=group:BUNDLE a1 d1
a=ice-options:trickle
m=audio 9 UDP/TLS/RTP/SAVPF 96 0 8 97 98
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=mid:a1
a=msid:QI39StLS8W7ZbQl1sJsWUXkr3Zf12fJUvzQ1
       QI39StLS8W7ZbQl1sJsWUXkr3Zf12fJUvzQ1a0
a=sendrecv
a=rtpmap:96 opus/48000/2
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:97 telephone-event/8000
a=rtpmap:98 telephone-event/48000
a=maxptime:120
a=ice-ufrag:7sFvz2gdLkEwjZEr
a=ice-pwd:dOTZKZNVlO9RSGsEGM63JXT2
a=fingerprint:sha-256 6B:8B:F0:65:5F:78:E2:51:3B:AC:6F:F3:3F:46:1B:35
                     :DC:B8:5F:64:1A:24:C2:43:F0:A1:58:D0:A1:2C:19:08
a=setup:active
a=rtcp-mux
a=rtcp-rsize
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=extmap:2 urn:ietf:params:rtp-hdrext:sdes:mid

m=application 9 UDP/DTLS/SCTP webrtc-datachannel
c=IN IP4 0.0.0.0
a=mid:d1
a=fmtp:webrtc-datachannel max-message-size=65536
a=sctp-port 5000
a=fingerprint:sha-256 6B:8B:F0:65:5F:78:E2:51:3B:AC:6F:F3:3F:46:1B:35
                     :DC:B8:5F:64:1A:24:C2:43:F0:A1:58:D0:A1:2C:19:08
a=setup:active

// candidate B3

candidate:109270924 1 udp 2122194687 192.168.2.3 61665 typ host

// candidate B4

candidate:4036177504 1 udp 1685987071 55.66.77.88 64532 typ srflx
          raddr 192.168.2.3 rport 61665

// offer B2

v=0
o=- 7729291447651054566 2 IN IP4 0.0.0.0
s=-
t=0 0
a=group:BUNDLE a1 d1 v1 v2
a=ice-options:trickle
m=audio 64532 UDP/TLS/RTP/SAVPF 96 0 8 97 98
c=IN IP4 55.66.77.88
a=rtcp:64532 IN IP4 55.66.77.88
a=mid:a1
a=msid:QI39StLS8W7ZbQl1sJsWUXkr3Zf12fJUvzQ1
       QI39StLS8W7ZbQl1sJsWUXkr3Zf12fJUvzQ1a0
a=sendrecv
a=rtpmap:96 opus/48000/2
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:97 telephone-event/8000
a=rtpmap:98 telephone-event/48000
a=maxptime:120
a=ice-ufrag:7sFvz2gdLkEwjZEr
a=ice-pwd:dOTZKZNVlO9RSGsEGM63JXT2
a=fingerprint:sha-256 6B:8B:F0:65:5F:78:E2:51:3B:AC:6F:F3:3F:46:1B:35
                     :DC:B8:5F:64:1A:24:C2:43:F0:A1:58:D0:A1:2C:19:08
a=setup:actpass
a=rtcp-mux
a=rtcp-rsize
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=extmap:2 urn:ietf:params:rtp-hdrext:sdes:mid
a=candidate:109270924 1 udp 2122194687 192.168.2.3 61665 typ host
a=candidate:4036177504 1 udp 1685987071 55.66.77.88 64532 typ srflx
            raddr 192.168.2.3 rport 61665
a=candidate:3671762467 1 udp 41819903 66.77.88.99 50416 typ relay
            raddr 55.66.77.88 rport 64532
a=end-of-candidates

m=application 64532 UDP/DTLS/SCTP webrtc-datachannel
c=IN IP4 55.66.77.88
a=mid:d1
a=fmtp:webrtc-datachannel max-message-size=65536
a=sctp-port 5000
a=ice-ufrag:7sFvz2gdLkEwjZEr
a=ice-pwd:dOTZKZNVlO9RSGsEGM63JXT2
a=fingerprint:sha-256 6B:8B:F0:65:5F:78:E2:51:3B:AC:6F:F3:3F:46:1B:35
                     :DC:B8:5F:64:1A:24:C2:43:F0:A1:58:D0:A1:2C:19:08
a=setup:actpass
a=candidate:109270924 1 udp 2122194687 192.168.2.3 61665 typ host
a=candidate:4036177504 1 udp 1685987071 55.66.77.88 64532 typ srflx
            raddr 192.168.2.3 rport 61665
a=candidate:3671762467 1 udp 41819903 66.77.88.99 50416 typ relay
            raddr 55.66.77.88 rport 64532
a=end-of-candidates

m=video 0 UDP/TLS/RTP/SAVPF 100 101
c=IN IP4 55.66.77.88
a=bundle-only
a=rtcp:64532 IN IP4 55.66.77.88
a=mid:v1
a=msid:61317484-2ed4-49d7-9eb7-1414322a7aae
       f30bdb4a-5db8-49b5-bcdc-e0c9a23172e0
a=sendrecv
a=rtpmap:100 VP8/90000
a=rtpmap:101 rtx/90000
a=fmtp:101 apt=100
a=fingerprint:sha-256
              19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04
             :BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2
a=setup:actpass
a=rtcp-mux
a=rtcp-rsize
a=extmap:2 urn:ietf:params:rtp-hdrext:sdes:mid
a=rtcp-fb:100 ccm fir
a=rtcp-fb:100 nack
a=rtcp-fb:100 nack pli

m=video 0 UDP/TLS/RTP/SAVPF 100 101
c=IN IP4 55.66.77.88
a=bundle-only
a=rtcp:64532 IN IP4 55.66.77.88
a=mid:v1
a=msid:71317484-2ed4-49d7-9eb7-1414322a7aae
       f30bdb4a-5db8-49b5-bcdc-e0c9a23172e0
a=sendrecv
a=rtpmap:100 VP8/90000
a=rtpmap:101 rtx/90000
a=fmtp:101 apt=100
a=fingerprint:sha-256
              19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04
             :BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2
a=setup:actpass
a=rtcp-mux
a=rtcp-rsize
a=extmap:2 urn:ietf:params:rtp-hdrext:sdes:mid
a=rtcp-fb:100 ccm fir
a=rtcp-fb:100 nack
a=rtcp-fb:100 nack pli

// answer B2

v=0
o=- 4962303333179871723 2 IN IP4 0.0.0.0
s=-
t=0 0
a=group:BUNDLE a1 d1 v1 v2
a=ice-options:trickle
m=audio 52546 UDP/TLS/RTP/SAVPF 96 0 8 97 98
c=IN IP4 11.22.33.44
a=rtcp:52546 IN IP4 11.22.33.44
a=mid:a1
a=msid:57017fee-b6c1-4162-929c-a25110252400
       e83006c5-a0ff-4e0a-9ed9-d3e6747be7d9
a=sendrecv
a=rtpmap:96 opus/48000/2
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:97 telephone-event/8000
a=rtpmap:98 telephone-event/48000
a=maxptime:120
a=ice-ufrag:ATEn1v9DoTMB9J4r
a=ice-pwd:AtSK0WpNtpUjkY4+86js7ZQl
a=fingerprint:sha-256
              19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04
             :BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2
a=setup:passive
a=rtcp-mux
a=rtcp-rsize
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=extmap:2 urn:ietf:params:rtp-hdrext:sdes:mid
a=candidate:109270923 1 udp 2122194687 192.168.1.2 51556 typ host
a=candidate:4036177503 1 udp 1685987071 11.22.33.44 52546 typ srflx
            raddr 192.168.1.2 rport 51556
a=candidate:3671762466 1 udp 41819903 22.33.44.55 61405 typ relay
            raddr 11.22.33.44 rport 52546
a=end-of-candidates

m=application 52546 UDP/DTLS/SCTP webrtc-datachannel
c=IN IP4 11.22.33.44
a=mid:d1
a=fmtp:webrtc-datachannel max-message-size=65536
a=sctp-port 5000
a=fingerprint:sha-256 19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04
                     :BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2
a=setup:passive

m=video 52546 UDP/TLS/RTP/SAVPF 100 101
c=IN IP4 11.22.33.44
a=rtcp:52546 IN IP4 11.22.33.44
a=mid:v1
a=recvonly
a=rtpmap:100 VP8/90000
a=rtpmap:101 rtx/90000
a=fmtp:101 apt=100
a=fingerprint:sha-256
              19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04
             :BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2
a=setup:passive
a=rtcp-mux
a=rtcp-rsize
a=extmap:2 urn:ietf:params:rtp-hdrext:sdes:mid
a=rtcp-fb:100 ccm fir
a=rtcp-fb:100 nack
a=rtcp-fb:100 nack pli

m=video 52546 UDP/TLS/RTP/SAVPF 100 101
c=IN IP4 11.22.33.44
a=rtcp:52546 IN IP4 11.22.33.44
a=mid:v2
a=recvonly
a=rtpmap:100 VP8/90000
a=rtpmap:101 rtx/90000
a=fmtp:101 apt=100
a=fingerprint:sha-256
              19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04
             :BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2
a=setup:passive
a=rtcp-mux
a=rtcp-rsize
a=extmap:2 urn:ietf:params:rtp-hdrext:sdes:mid
a=rtcp-fb:100 ccm fir
a=rtcp-fb:100 nack
a=rtcp-fb:100 nack pli