import argparse

class PeerConnection:
  SESSION_SDP = \
 """v=0
    o=- {0.session_id} {0.version} IN IP4 0.0.0.0
    s=-
    t=0 0
    a=ice-options:trickle
    a=group:BUNDLE a1 v1
    """
# TODO: allow configurable BUNDLE

  TRANSPORT_SDP_PRE_RTCP = \
 """a=ice-ufrag:{0[ice_ufrag]}
    a=ice-pwd:{0[ice_pwd]}
    a=fingerprint:sha-256 {0[dtls_fingerprint]}
    a=setup:{0[dtls_dir]}
    a=dtls-id:1
    """
  TRANSPORT_SDP_RTCP = \
 """a=rtcp:{0[local_rtcp]} IN IP4 {0[local_ip]}
    """
  TRANSPORT_SDP_POST_RTCP = \
 """a=rtcp-mux
    a=rtcp-rsize
    """
  TRANSPORT_SDP_WITH_RTCP = TRANSPORT_SDP_PRE_RTCP + TRANSPORT_SDP_RTCP + \
                            TRANSPORT_SDP_POST_RTCP
  TRANSPORT_SDP_NO_RTCP = TRANSPORT_SDP_PRE_RTCP + TRANSPORT_SDP_POST_RTCP
# TODO: rtcp-mux-only

  AUDIO_SDP = \
 """m=audio {0[local_port]} UDP/TLS/RTP/SAVPF 96 0 8 97 98
    c=IN IP4 {0[local_ip]}
    a=mid:{0[mid]}
    a=sendrecv
    a=rtpmap:96 opus/48000/2
    a=rtpmap:0 PCMU/8000
    a=rtpmap:8 PCMA/8000
    a=rtpmap:97 telephone-event/8000
    a=rtpmap:98 telephone-event/48000
    a=maxptime:120
    a=extmap:1 urn:ietf:params:rtp-hdrext:sdes:mid
    a=extmap:2 urn:ietf:params:rtp-hdrext:ssrc-audio-level
    a=msid:{0[ms]} {0[mst]}
    """
  # TODO: proper default candidate in c=, m=, rtcp lines

  VIDEO_SDP = \
 """m=video {0[local_port]} UDP/TLS/RTP/SAVPF 100 101
    c=IN IP4 {0[local_ip]}
    a=mid:{0[mid]}
    a=sendrecv
    a=rtpmap:100 VP8/90000
    a=rtpmap:101 rtx/90000
    a=fmtp:101 apt=100
    a=extmap:1 urn:ietf:params:rtp-hdrext:sdes:mid
    a=rtcp-fb:100 ccm fir
    a=rtcp-fb:100 nack
    a=rtcp-fb:100 nack pli
    a=msid:{0[ms]} {0[mst]}
    """

  DATA_SDP = \
 """m=application {0[local_port]} UDP/DTLS/SCTP webrtc-datachannel
    c=IN IP4 {0[local_ip]}
    a=mid:{0[mid]}
    a=max-message-size:65536
    a=sctp-port:5000
    """

  CANDIDATE_ATTR = 'candidate:{0} {1} {2} {3} {4} {5} typ {6}'
  CANDIDATE_ATTR_WITH_RADDR = CANDIDATE_ATTR + ' raddr {7} rport {8}'

  END_OF_CANDIDATES_SDP = \
 """a=end-of-candidates
    """

  def __init__(self, session_id, trickle, bundle_policy, mux_policy,
               local_ip, stun_ip, relay_ip, fingerprint, m_sections):
    self.session_id = session_id
    self.trickle = trickle
    self.bundle_policy = bundle_policy
    self.mux_policy = mux_policy
    self.local_ip = local_ip
    self.stun_ip = stun_ip
    self.relay_ip = relay_ip
    self.fingerprint = fingerprint
    self.m_sections = m_sections
    self.version = 0

  def create_candidate(self, component, type, addr, port, raddr, rport):
    if type == 'host':
      formatter = self.CANDIDATE_ATTR
      type_priority = 126
    elif type == 'srflx':
      formatter = self.CANDIDATE_ATTR_WITH_RADDR
      type_priority = 110
    else:
      formatter = self.CANDIDATE_ATTR_WITH_RADDR
      type_priority = 0
    foundation = 1
    protocol = 'udp'
    priority = type_priority << 24 | (256 - component)
    return 'a=' + formatter.format(foundation, component, protocol, priority,
                                   addr, port, type, raddr, rport) + '\n'

  def create_candidates(self, m_section, components):
    sdp = ''
    for i in range(0, components):
      sdp += self.create_candidate(i + 1, 'host',
                                   self.local_ip, m_section['local_port'] + i,
                                   None, None)
    if self.stun_ip:
      for i in range(0, components):
        sdp += self.create_candidate(i + 1, 'srflx',
                                     self.stun_ip, m_section['srflx_port'] + i,
                                     self.local_ip, m_section['local_port'] + i)
    if self.relay_ip:
      for i in range(0, components):
        sdp += self.create_candidate(i + 1, 'relay',
                                     self.relay_ip, m_section['relay_port'] + i,
                                     self.stun_ip, m_section['srflx_port'] + i)
    return sdp

  def create_m_sections(self, stype, mtype, formatter):
    sdp = ''
    num_components = 1
    if self.mux_policy == 'negotiate' and stype == 'offer':
      num_components = 2
    for m_section in self.m_sections:
      if m_section['type'] == mtype:
        copy = m_section.copy()
        copy['local_ip'] = self.local_ip
        # tricky way to make rtcp port be rtp + 1, only if offering non-mux
        copy['local_rtcp'] = copy['local_port'] + num_components - 1
        copy['dtls_fingerprint'] = self.fingerprint
        sdp += formatter.format(copy)
        # only put transport attribs into non-bundled m= sections
        if not 'bundled' in copy or not copy['bundled']:
          # only add a=rtcp attribute if we're not sure we're muxing
          if stype == 'offer':
            sdp += self.TRANSPORT_SDP_WITH_RTCP.format(copy)
          else:
            sdp += self.TRANSPORT_SDP_NO_RTCP.format(copy)
          # add candidates/eoc to SDP if we're not trickling
          if not self.trickle:
            sdp += self.create_candidates(copy, num_components)
            sdp += self.END_OF_CANDIDATES_SDP
    return sdp

  def create_sdp(self, type):
    self.version += 1
    sdp = self.SESSION_SDP.format(self)
    sdp += self.create_m_sections(type, 'audio', self.AUDIO_SDP)
    sdp += self.create_m_sections(type ,'video', self.VIDEO_SDP)
    sdp += self.create_m_sections(type, 'data', self.DATA_SDP)
    # clean up the leading whitespace in the constants
    sdp = sdp.replace('    ', '')
    cands = []
    return { 'type': type, 'sdp': sdp, 'candidates': cands }
  def create_offer(self):
    return self.create_sdp('offer')
  def create_answer(self):
    return self.create_sdp('answer')

def format_desc(desc):
  lines_pre = desc['sdp'].split('\n')[:-1]
  lines_post = []
  for line in lines_pre:
    if line[:2] == 'm=' and len(lines_post) > 0:
      # add blank line between m= sections
      lines_post.append('')
      lines_post.append(line)
    elif line[:6] == 'a=msid':
      # wrap long msid lines
      lines_post.append(line[:43])
      lines_post.append(' ' * 7 + line[44:83])
    elif line[:13] == 'a=fingerprint':
      # wrap long fingerprint lines
      lines_post.append(line[:21])
      lines_post.append(' ' * 14 + line[22:70])
      lines_post.append(' ' * 14 + line[70:117])
    else:
      lines_post.append(line)
  return lines_post

def replace_desc(name, desc_lines, draft):
  # update the samples in-place in the draft
  draft_copy = draft[:]
  del draft[:]
  found = False
  for draft_line in draft_copy:
    if found and '</artwork>' in draft_line:
      for desc_line in desc_lines:
        draft.append(desc_line + '\n')
      draft.append(']]>\n')
      found = False
    if not found:
      draft.append(draft_line)
    if ('<artwork alt="' + name + '">') in draft_line:
      found = True
      draft.append('<![CDATA[\n')

def output_desc(name, desc, draft):
  formatted_lines = format_desc(desc)
  if draft:
    replace_desc(name, formatted_lines, draft)
  else:
    print '\n'.join(formatted_lines)

def example1(draft):
  ms1 = [
    { 'type': 'audio', 'mid': 'a1',
      'ms': '47017fee-b6c1-4162-929c-a25110252400',
      'mst': 'f83006c5-a0ff-4e0a-9ed9-d3e6747be7d9',
      'local_port': 56500, 'ice_ufrag': 'ETEn',
      'ice_pwd': 'OtSK0WpNtpUjkY4+86js7ZQl', 'dtls_dir': 'actpass' },
    { 'type': 'video', 'mid': 'v1',
      'ms': '47017fee-b6c1-4162-929c-a25110252400',
      'mst': 'f30bdb4a-5db8-49b5-bcdc-e0c9a23172e0',
      'local_port': 56502, 'ice_ufrag': 'BGKk',
      'ice_pwd': 'mqyWsAjvtKwTGnvhPztQ9mIf', 'dtls_dir': 'actpass' }
  ]
  fp1 = '19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04:BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2'
  pc1 = PeerConnection(session_id = '4962303333179871722', trickle = False,
                       bundle_policy = 'balanced', mux_policy = 'negotiate',
                       local_ip = '192.0.2.1', stun_ip = None, relay_ip = None,
                       fingerprint = fp1, m_sections = ms1)

  ms2 = [
    { 'type': 'audio', 'mid': 'a1',
      'ms': '61317484-2ed4-49d7-9eb7-1414322a7aae',
      'mst': '5a7b57b8-f043-4bd1-a45d-09d4dfa31226',
      'local_port': 34300, 'ice_ufrag': '6sFv',
      'ice_pwd': 'cOTZKZNVlO9RSGsEGM63JXT2', 'dtls_dir': 'active' },
    { 'type': 'video', 'mid': 'v1',
      'ms': '61317484-2ed4-49d7-9eb7-1414322a7aae',
      'mst': '4ea4d4a1-2fda-4511-a9cc-1b32c2e59552',
      'local_port': 34300, 'bundled': True }
  ]
  fp2 = '6B:8B:F0:65:5F:78:E2:51:3B:AC:6F:F3:3F:46:1B:35:DC:B8:5F:64:1A:24:C2:43:F0:A1:58:D0:A1:2C:19:08'
  pc2 = PeerConnection(session_id = '6729291447651054566', trickle = False,
                       bundle_policy = 'balanced', mux_policy = 'negotiate',
                       local_ip = '192.0.2.2', stun_ip = None, relay_ip = None,
                       fingerprint = fp2, m_sections = ms2)
  o = pc1.create_offer()
  output_desc('offer-A1', o, draft)
  a = pc2.create_answer()
  output_desc('answer-A1', a, draft)

def example2():
  pc1 = PeerConnection(trickle = True, bundle_policy = 'max-bundle',
                       mux_policy = 'require')
  pc2 = PeerConnection(trickle = False, bundle_policy = 'max-bundle',
                       mux_policy = 'require')
  o = pc1.create_offer()
  print_desc(o)
  a = pc2.create_answer()
  print_desc(a)

  #pc1.m_sections.append(new_video)
  o = pc2.create_offer()
  print_desc(o)
  a = pc1.create_answer()
  print_desc(a)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--replace', type=str)
  args = parser.parse_args()

  draft = None
  if args.replace:
    f = open(args.replace, 'r')
    draft = f.readlines()

  example1(draft)
  #example2(draft)

  if args.replace:
    f = open(args.replace, 'w')
    f.writelines(draft)

if __name__ == '__main__':
  main()
