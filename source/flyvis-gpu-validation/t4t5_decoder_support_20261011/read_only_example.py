"""Preview existing accepted arrays. No model import or new computation."""
import argparse
import json
import sys

from service import AcceptedReferenceCache

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference', choices=['camera609_Full', 'G2_edge0_180_Full', 'edge0_180_decoder_preview'], default='camera609_Full')
    args = parser.parse_args()
    cache = AcceptedReferenceCache()
    identity = cache.registry['references'][args.reference]['identity']
    a, receipt = cache.open(args.reference, identity)
    print(json.dumps(dict(receipt, shape=list(a.shape), dtype=str(a.dtype), read_only=not a.flags.writeable,
                         first_value=float(a.flat[0]), torch_imported='torch' in sys.modules), indent=2))
