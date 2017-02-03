import base64
import random
import sys
import uuid

FORMAT_STR1 = """\
  ms{0[num]} = [
    {{ 'type': 'audio', 'mid': 'a1',
      'ms': '{0[ms]}',
      'mst': '{0[msta]}',
      'local_port': {0[lp]}, 'srflx_port': {0[sp]}, 'relay_port': {0[rp]},
      'ice_ufrag': '{0[ufrag]}', 'ice_pwd': '{0[pwd]}',
      'dtls_dir': '{0[ddir]}' }},
    {{ 'type': 'video', 'mid': 'v1',
      'ms': '{0[ms]}',
      'mst': '{0[mstv]}' }}
  ]
  fp{0[num]}  = '{0[fp]}'
  pc{0[num]}  = PeerConnection(session_id = '{0[id]}', trickle = True,
                       bundle_policy = 'max-bundle', mux_policy = 'require',
                       ip_last_quad = {0[ip]}, fingerprint = fp{0[num]}, m_sections = ms{0[num]})
"""

FORMAT_STR2 = """\
  o = pc1.create_offer()
  output_desc('offer-{0}1', o, draft)
  a = pc2.create_answer()
  output_desc('answer-{0}1', a, draft)
"""

def random_bytes(bytes):
  return ''.join(chr(random.getrandbits(8)) for _ in range(bytes))

def random_uuid_str():
  return uuid.UUID(bytes=random_bytes(16))

def make_obj(num):
  return {
    'num':   num,
    'id':    random.getrandbits(63),
    'ip':    num * 100,
    'fp':    ':'.join('%02x' % ord(b) for b in random_bytes(16)).upper(),
    'ufrag': base64.b64encode(random_bytes(3)),
    'pwd':   base64.b64encode(random_bytes(18)),
    'ddir':  ['passive', 'active'][num - 1],
    'ms':    random_uuid_str(),
    'msta':  random_uuid_str(),
    'mstv':  random_uuid_str(),
    'lp':    10000 + num * 100,
    'sp':    11000 + num * 100,
    'rp':    12000 + num * 100,
  }

def main():
  # Use the example name as a seed
  if len(sys.argv) > 1:
    letter = sys.argv[1]
  else:
    letter = 'X'
  random.seed(ord(letter))
  print FORMAT_STR1.format(make_obj(1))
  print FORMAT_STR1.format(make_obj(2))
  print FORMAT_STR2.format(letter)

if __name__ == '__main__':
  main()
