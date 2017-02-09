# TODO: LS for offer-B1 (should omit?) and answer-B2 (should have v1?)
# TODO: add relay candidates (for A1)
import argparse

class PeerConnection:
  SESSION_SDP = \
 """v=0
    o=- {0.session_id} {0.version} IN IP4 0.0.0.0
    s=-
    t=0 0
    a=ice-options:trickle
    a=group:BUNDLE {1}
    a=group:LS {2}
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
    a=imageattr:100 recv [x=[48:1920],y=[48:1080],q=1.0]
    a=extmap:1 urn:ietf:params:rtp-hdrext:sdes:mid
    a=rtcp-fb:100 ccm fir
    a=rtcp-fb:100 nack
    a=rtcp-fb:100 nack pli
    a=msid:{0[ms]} {0[mst]}
    a=rid:1 send
    a=rid:2 send
    a=rid:3 send
    a=simulcast:send 1;2;3
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
    a=rtcp-mux-only
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
    self.host_ip = '203.0.113.' + str(ip_last_quad)
    self.srflx_ip = '198.51.100.' + str(ip_last_quad)
    self.relay_ip = '192.0.2.' + str(ip_last_quad)
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
        default_port = self.get_port(m_section, 'host_port')
        default_ip = self.host_ip
      # tricky way to make rtcp port be rtp + 1, only if offering non-mux
      default_rtcp = default_port + num_components - 1

    m_section['default_ip'] = default_ip
    m_section['default_port'] = default_port
    m_section['default_rtcp'] = default_rtcp

  def remove_attribute(self, sdp, attrib):
    # look for the whole attribute, to avoid finding a=rtcp inside of a=rtcp-mux
    start = sdp.find(attrib + ':')
    if start == -1:
      start = sdp.find(attrib + '\n')
    if start == -1:
      return sdp

    end = sdp.find('\n', start)
    return sdp[:start] + sdp[end + 1:]

  def create_media_formatter(self, type, want_transport,
                             want_bundle_only, want_rtcp,
                             want_rtcp_mux_only):
    formatter = self.MEDIA_TABLE[type]
    if want_transport:
      formatter += self.TRANSPORT_SDP
    if want_bundle_only:
      formatter += self.BUNDLE_ONLY_SDP
    if not want_rtcp:
      formatter = self.remove_attribute(formatter, 'a=rtcp')
    if not want_rtcp_mux_only:
      formatter = self.remove_attribute(formatter, 'a=rtcp-mux-only')
    return formatter

  # creates 'candidate:1 1 udp 999999 1.1.1.1:1111 type host'
  def create_candidate_attr(self, component, type, addr, port, raddr, rport):
    TYPE_PRIORITIES = {'host': 126, 'srflx': 110, 'relay': 0}
    if raddr:
      formatter = self.CANDIDATE_ATTR_WITH_RADDR
    else:
      formatter = self.CANDIDATE_ATTR
    foundation = 1
    protocol = 'udp'
    priority = TYPE_PRIORITIES[type] << 24 | (256 - component)
    return formatter.format(foundation, component, protocol, priority,
                            addr, port, type, raddr, rport)

  # creates {'ufrag': 'wzyz', 'index':0, 'mid':'a1', 'attr': 'candidate:blah'}
  def create_candidate_obj(self, ufrag, index, mid,
                           component, type, addr, port, raddr, rport):
    return {'ufrag': ufrag, 'index': index, 'mid': mid,
            'attr': self.create_candidate_attr(component, type, addr, port,
                                                    raddr, rport) }

  # if port exists of type |type|, returns list of candidates with size |num|
  def maybe_create_candidates_of_type(self, m_section, index, num, type, rtype):
    candidates = []
    port = self.get_port(m_section, type + '_port')
    if port:
      addr = getattr(self, type + '_ip')
      if rtype:
        # srflx/relay candidates; 0.0.0.0 if no related candidate
        rport = self.get_port(m_section, rtype + '_port')
        if rport:
          raddr = getattr(self, rtype + '_ip')
        else:
          rport = 0
          raddr = '0.0.0.0'
      else:
        # host candidates
        rport = 0
        raddr = None

      for i in range(0, num):
        candidates.append(self.create_candidate_obj(
          m_section['ice_ufrag'], index, m_section['mid'],
          i + 1, type, addr, port + i, raddr, rport + i))

    return candidates

  def create_candidates(self, m_section, index, num):
    candidates = []
    candidates.extend(
      self.maybe_create_candidates_of_type(m_section, index, num, 'host', None))
    candidates.extend(
      self.maybe_create_candidates_of_type(m_section, index, num, 'srflx',
                                           'host'))
    candidates.extend(
      self.maybe_create_candidates_of_type(m_section, index, num, 'relay',
                                           'srflx'))
    return candidates

  def add_m_section(self, desc, m_section):
    stype = desc['type']
    index = self.m_sections.index(m_section)
    bundled = not 'ice_ufrag' in m_section
    bundle_only = bundled and self.version == 1 and stype == 'offer'
    num_components = 1
    if self.mux_policy == 'negotiate' and stype == 'offer':
      num_components = 2
    rtcp_mux_only = self.mux_policy == 'require'

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
                                            want_rtcp = num_components == 2,
                                            want_rtcp_mux_only = rtcp_mux_only)
    sdp = formatter.format(copy)

    # if not bundling, create candidates either in SDP or separately
    if not bundled:
      candidates = self.create_candidates(copy, index, num_components)
      if not self.trickle or self.version > 1:
        for candidate in candidates:
          sdp += 'a=' + candidate['attr'] + '\n'
        sdp += self.END_OF_CANDIDATES_SDP
      else:
        desc['candidates'].extend(candidates)

    desc['sdp'] += sdp

  def create_desc(self, type):
    self.version += 1
    bundle_list = [m_section['mid'] for m_section in self.m_sections]
    bundle_group = ' '.join(bundle_list)
    ls_list = [m_section['mid'] for m_section in self.m_sections if
               'ms' in m_section and
               m_section['ms'] == self.m_sections[0]['ms']]
    ls_group = ' '.join(ls_list)

    desc = { 'type': type, 'sdp': '', 'candidates': [] }
    desc['sdp'] = self.SESSION_SDP.format(self, bundle_group, ls_group)
    for m_section in self.m_sections:
      self.add_m_section(desc, m_section)
    # clean up the leading whitespace in the constants
    desc['sdp'] = desc['sdp'].replace('    ', '')
    return desc
  def create_offer(self):
    return self.create_desc('offer')
  def create_answer(self):
    return self.create_desc('answer')

def split_line(line, *positions):
  lines = []
  indent = 0
  last_pos = 0
  if len(line) > 72:
    for pos in positions:
      if pos == -1:
        break
      lines.append(' ' * indent + line[last_pos:pos].strip())
      if indent == 0:
        indent = line.find(':') + 1
      last_pos = pos

  lines.append(' ' * indent + line[last_pos:].strip())
  return lines

def format_sdp(sdp):
  lines_pre = sdp.split('\n')[:-1]
  lines_post = []
  for line in lines_pre:
    if line.startswith('m=') and len(lines_post) > 0:
      # add blank line between m= sections
      lines_post.append('')
      lines_post.append(line)
    elif line.startswith('a=msid'):
      # wrap long msid lines
      lines_post.extend(split_line(line, line.find(' ')))
    elif line.startswith('a=fingerprint'):
      # wrap long fingerprint lines
      lines_post.extend(split_line(line, 21, 70))
    elif line.startswith('a=candidate'):
      # wrap long candidate lines
      lines_post.extend(split_line(line, line.find('raddr')))
    else:
      lines_post.append(line)
  return lines_post

# turn a candidate object into something like
# ufrag 7sFv
# index 0
# mid   a1
# attr  candidate:1 1 udp 255 66.77.88.99 50416 typ relay
#                 raddr 55.66.77.88 rport 64532
def format_candidate(cand_obj):
  lines = []
  for key in ['ufrag', 'index', 'mid', 'attr']:
    if key != 'attr':
      lines.append('{0: <5} {1}'.format(key, cand_obj[key]))
    else:
      attr_line = 'attr  ' + cand_obj['attr']
      lines.extend(split_line(attr_line, attr_line.find('raddr')))
  return lines

# update a specific <artwork/> in-place in the draft
def replace_artwork(draft_lines, name, artwork_lines):
  draft_copy = draft_lines[:]
  del draft_lines[:]
  found = False
  for draft_line in draft_copy:
    if found and '</artwork>' in draft_line:
      for artwork_line in artwork_lines:
        draft_lines.append(artwork_line + '\n')
      draft_lines.append(']]>\n')
      found = False
    if not found:
      draft_lines.append(draft_line)
    if ('<artwork alt="' + name + '">') in draft_line:
      found = True
      draft_lines.append('<![CDATA[\n')

# update a sample in-place in the draft
def replace_desc(draft_lines, name, desc):
  replace_artwork(draft_lines, name, format_sdp(desc['sdp']))
  for i, candidate in enumerate(desc['candidates']):
    candidate_name = name + '-candidate-' + str(i + 1)
    replace_artwork(draft_lines, candidate_name, format_candidate(candidate))

def print_desc(name, desc):
  print '[' + name + ']'
  print '\n'.join(format_sdp(desc['sdp']))
  print
  for i, candidate in enumerate(desc['candidates']):
    print '[' + name + ' candidate ' + str(i + 1) + ']'
    print '\n'.join(format_candidate(candidate))
    print

def output_desc(name, desc, draft_lines):
  if draft_lines:
    replace_desc(draft_lines, name, desc)
  else:
    print_desc(name, desc)

def simple_example(draft):
  ms1 = [
    { 'type': 'audio', 'mid': 'a1',
      'ms': '47017fee-b6c1-4162-929c-a25110252400',
      'mst': 'f83006c5-a0ff-4e0a-9ed9-d3e6747be7d9',
      'host_port': 10100, 'ice_ufrag': 'ETEn',
      'ice_pwd': 'OtSK0WpNtpUjkY4+86js7ZQl', 'dtls_dir': 'passive' },
    { 'type': 'video', 'mid': 'v1',
      'ms': '47017fee-b6c1-4162-929c-a25110252400',
      'mst': 'f30bdb4a-5db8-49b5-bcdc-e0c9a23172e0',
      'host_port': 10102, 'ice_ufrag': 'BGKk',
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
      'host_port': 10200, 'ice_ufrag': '6sFv',
      'ice_pwd': 'cOTZKZNVlO9RSGsEGM63JXT2', 'dtls_dir': 'active' },
    { 'type': 'video', 'mid': 'v1',
      'ms': '61317484-2ed4-49d7-9eb7-1414322a7aae',
      'mst': '4ea4d4a1-2fda-4511-a9cc-1b32c2e59552',
      'host_port': 10200 }
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
      'host_port': 10100, 'srflx_port': 11100, 'relay_port': 12100,
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
      'host_port': 10200, 'srflx_port': 11200, 'relay_port': 12200,
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
    { 'type': 'video', 'mid': 'v1', 'ms': '-',
      'mst': '08575c88-be1f-42d0-8717-5d7f77b57b20',
      'direction': 'recvonly' },
    { 'type': 'video', 'mid': 'v2', 'ms': '-',
      'mst': '8dfffea7-c7d6-4036-86bd-98c59391f8a3',
      'direction': 'recvonly' },
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
      'ms': 'bbce3ba6-abfc-ac63-d00a-e15b286f8fce',
      'mst': 'e80098db-7159-3c06-229a-00df2a9b3dbc',
      'relay_port': 12100,
      'ice_ufrag': '4ZcD', 'ice_pwd': 'ZaaG6OG7tCn4J/lehAGz+HHD',
      'dtls_dir': 'passive' },
    { 'type': 'video', 'mid': 'v1',
      'ms': 'bbce3ba6-abfc-ac63-d00a-e15b286f8fce',
      'mst': 'ac701365-eb06-42df-cc93-7f22bc308789' }
  ]
  fp1  = 'C4:68:F8:77:6A:44:F1:98:6D:7C:9F:47:EB:E3:34:A4:0A:AA:2D:49:08:28:70:2E:1F:AE:18:7D:4E:3E:66:BF'
  pc1  = PeerConnection(session_id = '1070771854436052752', trickle = True,
                       bundle_policy = 'max-bundle', mux_policy = 'require',
                       ip_last_quad = 100, fingerprint = fp1, m_sections = ms1)

  ms2 = [
    { 'type': 'audio', 'mid': 'a1',
      'ms': '751f239e-4ae0-c549-aa3d-890de772998b',
      'mst': '04b5a445-82cc-c9e8-9ffe-c24d0ef4b0ff',
      'direction': 'sendonly',
      'relay_port': 12200,
      'ice_ufrag': 'TpaA', 'ice_pwd': 't2Ouhc67y8JcCaYZxUUTgKw/',
      'dtls_dir': 'active' },
    { 'type': 'video', 'mid': 'v1',
      'ms': '751f239e-4ae0-c549-aa3d-890de772998b',
      'mst': '39292672-c102-d075-f580-5826f31ca958',
      'direction': 'sendonly' }
  ]
  fp2  = 'A2:F3:A5:6D:4C:8C:1E:B2:62:10:4A:F6:70:61:C4:FC:3C:E0:01:D6:F3:24:80:74:DA:7C:3E:50:18:7B:CE:4D'
  pc2  = PeerConnection(session_id = '6386516489780559513', trickle = True,
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
