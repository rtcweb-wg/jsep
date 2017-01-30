# TODO: LS groups
# TODO: msid for recvonly case?
# TODO: rtcp-mux-only
# TODO: output/replace candidates
import argparse

class PeerConnection:
  SESSION_SDP = \
 """v=0
    o=- {0.session_id} {0.version} IN IP4 0.0.0.0
    s=-
    t=0 0
    a=ice-options:trickle
    a=group:BUNDLE {1}
    """

  AUDIO_SDP = \
 """m=audio {0[default_port]} UDP/TLS/RTP/SAVPF 96 0 8 97 98
    c=IN IP4 {0[default_ip]}
    a=mid:{0[mid]}
    a={0[direction]}
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

  VIDEO_SDP = \
 """m=video {0[default_port]} UDP/TLS/RTP/SAVPF 100 101
    c=IN IP4 {0[default_ip]}
    a=mid:{0[mid]}
    a={0[direction]}
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
 """m=application {0[default_port]} UDP/DTLS/SCTP webrtc-datachannel
    c=IN IP4 {0[default_ip]}
    a=mid:{0[mid]}
    a=sctp-port:5000
    a=max-message-size:65536
    """

  MEDIA_TABLE = {
    'audio': AUDIO_SDP, 'video': VIDEO_SDP, 'application': DATA_SDP
  }

  TRANSPORT_SDP = \
 """a=ice-ufrag:{0[ice_ufrag]}
    a=ice-pwd:{0[ice_pwd]}
    a=fingerprint:sha-256 {0[dtls_fingerprint]}
    a=setup:{0[dtls_dir]}
    a=dtls-id:1
    a=rtcp:{0[default_rtcp]} IN IP4 {0[default_ip]}
    a=rtcp-mux
    a=rtcp-rsize
    """

  BUNDLE_ONLY_SDP = 'a=bundle-only\n'

  CANDIDATE_ATTR = 'candidate:{0} {1} {2} {3} {4} {5} typ {6}'
  CANDIDATE_ATTR_WITH_RADDR = CANDIDATE_ATTR + ' raddr {7} rport {8}'

  END_OF_CANDIDATES_SDP = 'a=end-of-candidates\n'

  def __init__(self, session_id, trickle, bundle_policy, mux_policy,
               ip_last_quad, fingerprint, m_sections):
    self.session_id = session_id
    self.trickle = trickle
    self.bundle_policy = bundle_policy
    self.mux_policy = mux_policy
    self.fingerprint = fingerprint
    self.m_sections = m_sections
    # IETF-approved example IPs
    self.local_ip = '203.0.113.' + str(ip_last_quad)
    self.stun_ip = '198.51.100.' + str(ip_last_quad)
    self.relay_ip = '192.0.2.200.' + str(ip_last_quad)
    self.version = 0

  def get_port(self, m_section, type):
    # get port from current section, bundle section, or None if type disallowed
    if type in m_section:
      return m_section[type]
    elif type in self.m_sections[0]:
      return self.m_sections[0][type]
    return None

  def select_default_candidates(self, m_section, bundle_only, num_components):
    if self.trickle and self.version == 1:
      default_ip = '0.0.0.0'
      if not bundle_only:
        default_port = default_rtcp = 9
      else:
        default_port = default_rtcp = 0
    else:
      default_port = self.get_port(m_section, 'relay_port')
      if default_port:
        default_ip = self.relay_ip
      else:
        default_port = self.get_port(m_section, 'local_port')
        default_ip = self.local_ip
      # tricky way to make rtcp port be rtp + 1, only if offering non-mux
      default_rtcp = default_port + num_components - 1
    m_section['default_ip'] = default_ip
    m_section['default_port'] = default_port
    m_section['default_rtcp'] = default_rtcp

  def remove_attribute(self, sdp, attrib):
    start = sdp.find(attrib + ':')
    if start == -1:
      return sdp

    end = sdp.find('\n', start)
    return sdp[:start] + sdp[end + 1:]

  def create_media_formatter(self, type, want_transport,
                             want_bundle_only, want_rtcp):
    formatter = self.MEDIA_TABLE[type]
    if want_transport:
      formatter += self.TRANSPORT_SDP
    if want_bundle_only:
      formatter += self.BUNDLE_ONLY_SDP
    if not want_rtcp:
      formatter = self.remove_attribute(formatter, 'a=rtcp')
    return formatter

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
    if 'local_port' in m_section:
      for i in range(components):
        sdp += self.create_candidate(i + 1, 'host',
                                     self.local_ip, m_section['local_port'] + i,
                                     None, None)
    if 'srflx_port' in m_section:
      for i in range(components):
        sdp += self.create_candidate(i + 1, 'srflx',
                                     self.stun_ip, m_section['srflx_port'] + i,
                                     self.local_ip, m_section['local_port'] + i)
    if 'relay_port' in m_section:
      for i in range(components):
        sdp += self.create_candidate(i + 1, 'relay',
                                     self.relay_ip, m_section['relay_port'] + i,
                                     self.stun_ip, m_section['srflx_port'] + i)
    return sdp

  def create_m_section(self, stype, m_section):
    bundled = not 'ice_ufrag' in m_section
    bundle_only = bundled and self.version == 1 and stype == 'offer'
    num_components = 1
    if self.mux_policy == 'negotiate' and stype == 'offer':
      num_components = 2

    copy = m_section.copy()
    self.select_default_candidates(copy, bundle_only, num_components)
    copy['dtls_fingerprint'] = self.fingerprint
    # always use actpass in offers
    if stype == 'offer':
      copy['dtls_dir'] = 'actpass'
    if copy['type'] != 'application':
      if 'direction' not in copy:
        copy['direction'] = 'sendrecv'

    # create the right template and fill it in
    formatter = self.create_media_formatter(copy['type'],
                                            want_transport = not bundled,
                                            want_bundle_only = bundle_only,
                                            want_rtcp = num_components == 2)
    sdp = formatter.format(copy)

    # add candidates/eoc to SDP if we're not trickling
    if not bundled and (not self.trickle or self.version > 1):
      sdp += self.create_candidates(copy, num_components)
      sdp += self.END_OF_CANDIDATES_SDP

    return sdp

  def create_m_sections(self, stype):
    sdp = ''
    for m_section in self.m_sections:
      sdp += self.create_m_section(stype, m_section)
    return sdp

  def create_sdp(self, type):
    self.version += 1
    bundle_sections = [m_section['mid'] for m_section in self.m_sections]
    sdp = self.SESSION_SDP.format(self, ' '.join(bundle_sections))
    sdp += self.create_m_sections(type)
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
      frags = line.split(' ')
      lines_post.append(frags[0])
      lines_post.append(' ' * 7 + frags[1])
    elif line[:13] == 'a=fingerprint':
      # wrap long fingerprint lines
      lines_post.append(line[:21])
      lines_post.append(' ' * 14 + line[22:70])
      lines_post.append(' ' * 14 + line[70:])
    elif line[:11] == 'a=candidate' and 'raddr' in line:
      frags = line.split('raddr')
      lines_post.append(frags[0])
      lines_post.append(' ' * 12 + frags[1])
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
    print '[' + name + ']'
    print '\n'.join(formatted_lines)
    print

def simple_example(draft):
  ms1 = [
    { 'type': 'audio', 'mid': 'a1',
      'ms': '47017fee-b6c1-4162-929c-a25110252400',
      'mst': 'f83006c5-a0ff-4e0a-9ed9-d3e6747be7d9',
      'local_port': 56500, 'ice_ufrag': 'ETEn',
      'ice_pwd': 'OtSK0WpNtpUjkY4+86js7ZQl', 'dtls_dir': 'passive' },
    { 'type': 'video', 'mid': 'v1',
      'ms': '47017fee-b6c1-4162-929c-a25110252400',
      'mst': 'f30bdb4a-5db8-49b5-bcdc-e0c9a23172e0',
      'local_port': 56502, 'ice_ufrag': 'BGKk',
      'ice_pwd': 'mqyWsAjvtKwTGnvhPztQ9mIf', 'dtls_dir': 'passive' }
  ]
  fp1 = '19:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04:BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2'
  pc1 = PeerConnection(session_id = '4962303333179871722', trickle = False,
                       bundle_policy = 'balanced', mux_policy = 'negotiate',
                       ip_last_quad = 100, fingerprint = fp1, m_sections = ms1)

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
                       ip_last_quad = 200, fingerprint = fp2, m_sections = ms2)

  o = pc1.create_offer()
  output_desc('offer-A1', o, draft)
  a = pc2.create_answer()
  output_desc('answer-A1', a, draft)

def complex_example(draft):
  ms1 = [
    { 'type': 'audio', 'mid': 'a1',
      'ms': '57017fee-b6c1-4162-929c-a25110252400',
      'mst': 'e83006c5-a0ff-4e0a-9ed9-d3e6747be7d9',
      'local_port': 51556, 'srflx_port': 52546, 'relay_port': 61405,
      'ice_ufrag': 'ATEn', 'ice_pwd': 'AtSK0WpNtpUjkY4+86js7ZQl',
      'dtls_dir': 'passive' },
    { 'type': 'application', 'mid': 'd1' }
  ]
  fp1 = '29:E2:1C:3B:4B:9F:81:E6:B8:5C:F4:A5:A8:D8:73:04:BB:05:2F:70:9F:04:A9:0E:05:E9:26:33:E8:70:88:A2'
  pc1 = PeerConnection(session_id = '4962303333179871723', trickle = True,
                       bundle_policy = 'max-bundle', mux_policy = 'require',
                       ip_last_quad = 100, fingerprint = fp1, m_sections = ms1)

  ms2 = [
    { 'type': 'audio', 'mid': 'a1',
      'ms': '71317484-2ed4-49d7-9eb7-1414322a7aae',
      'mst': '6a7b57b8-f043-4bd1-a45d-09d4dfa31226',
      'local_port': 61665, 'srflx_port': 64532, 'relay_port': 50416,
      'ice_ufrag': '7sFv', 'ice_pwd': 'dOTZKZNVlO9RSGsEGM63JXT2',
      'dtls_dir': 'active' },
    { 'type': 'application', 'mid': 'd1' }
  ]
  fp2 = '7B:8B:F0:65:5F:78:E2:51:3B:AC:6F:F3:3F:46:1B:35:DC:B8:5F:64:1A:24:C2:43:F0:A1:58:D0:A1:2C:19:08'
  pc2 = PeerConnection(session_id = '7729291447651054566', trickle = True,
                       bundle_policy = 'max-bundle', mux_policy = 'require',
                       ip_last_quad = 200, fingerprint = fp2, m_sections = ms2)

  o = pc1.create_offer()
  output_desc('offer-B1', o, draft)
  a = pc2.create_answer()
  output_desc('answer-B1', a, draft)

  ms1_video = [
    { 'type': 'video', 'mid': 'v1', 'ms': '-', 'mst': '-' },
    { 'type': 'video', 'mid': 'v2', 'ms': '-', 'mst': '-' }
  ]
  ms2_video = [
    { 'type': 'video', 'mid': 'v1',
      'ms': '71317484-2ed4-49d7-9eb7-1414322a7aae',
      'mst': '5ea4d4a1-2fda-4511-a9cc-1b32c2e59552' },
    { 'type': 'video', 'mid': 'v2',
      'ms': '81317484-2ed4-49d7-9eb7-1414322a7aae',
      'mst': '6ea4d4a1-2fda-4511-a9cc-1b32c2e59552' }
  ]

  pc1.m_sections.extend(ms1_video)
  pc2.m_sections.extend(ms2_video)
  o = pc2.create_offer()
  output_desc('offer-B2', o, draft)
  a = pc1.create_answer()
  output_desc('answer-B2', a, draft)

def warmup_example(draft):
  ms1 = [
    { 'type': 'audio', 'mid': 'a1',
      'ms': '19e2cea2-322b-4101-8c26-563145f5cd75',
      'mst': '34bf3719-2962-40af-a600-ad13f8de22d2',
      'local_port': 10100, 'srflx_port': 11100, 'relay_port': 12100,
      'ice_ufrag': 'R2hU', 'ice_pwd': '3JmmPxLZHHb/7n3hR93ucc8e',
      'dtls_dir': 'passive' },
    { 'type': 'video', 'mid': 'v1',
      'ms': '19e2cea2-322b-4101-8c26-563145f5cd75',
      'mst': '218e61be-6c3f-4784-a06d-92421699fb55' }
  ]
  fp1  = '12:EF:2E:A5:6E:15:B6:78:F5:A2:37:97:EC:9D:60:63'
  pc1  = PeerConnection(session_id = '3224496941647739038', trickle = True,
                       bundle_policy = 'max-bundle', mux_policy = 'require',
                       ip_last_quad = 100, fingerprint = fp1, m_sections = ms1)

  ms2 = [
    { 'type': 'audio', 'mid': 'a1',
      'ms': '3a0301bb-d0fa-4bf8-9ad4-86fbdf9f3aba',
      'mst': '49c4f187-f00c-4dfc-9e51-dea2267f6899',
      'direction': 'sendonly',
      'local_port': 10200, 'srflx_port': 11200, 'relay_port': 12200,
      'ice_ufrag': 'M4Wh', 'ice_pwd': 'ogwcYFAXKMJ6OjYAEV8dy6yj',
      'dtls_dir': 'active' },
    { 'type': 'video', 'mid': 'v1',
      'ms': '3a0301bb-d0fa-4bf8-9ad4-86fbdf9f3aba',
      'mst': '22675448-5025-4283-bd51-3c876a0959c5',
      'direction': 'sendonly' }
  ]
  fp2  = 'D4:7C:F0:46:10:D9:5F:90:5C:DB:DD:17:2C:38:45:BC'
  pc2  = PeerConnection(session_id = '7184966905803596701', trickle = True,
                       bundle_policy = 'max-bundle', mux_policy = 'require',
                       ip_last_quad = 200, fingerprint = fp2, m_sections = ms2)

  o = pc1.create_offer()
  output_desc('offer-C1', o, draft)
  a = pc2.create_answer()
  output_desc('answer-C1', a, draft)

  # change direction for reoffer
  for m_section in pc2.m_sections:
    m_section['direction'] = 'sendrecv'

  # TODO: do an ICE restart
  # pc2.m_sections[0].ice_ufrag = 'XXXX'
  # pc2.m_sections[0].ice_pwd = 'XXXX'
  # pc1.m_sections[0].ice_ufrag = 'YYYY'
  # pc1.m_sections[0].ice_pwd = 'YYYY'
  o = pc2.create_offer()
  output_desc('offer-C2', o, draft)
  a = pc1.create_answer()
  output_desc('answer-C2', a, draft)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--replace', type=str)
  args = parser.parse_args()

  draft = None
  if args.replace:
    f = open(args.replace, 'r')
    draft = f.readlines()

  simple_example(draft)
  complex_example(draft)
  warmup_example(draft)

  if args.replace:
    f = open(args.replace, 'w')
    f.writelines(draft)

if __name__ == '__main__':
  main()
